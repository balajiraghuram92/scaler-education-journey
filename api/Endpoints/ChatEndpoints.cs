using System;
using System.Collections.Generic;
using System.Linq;
using System.Security.Claims;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Routing;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Data;
using StudyTracker.Api.Models;
using StudyTracker.Api.Options;
using StudyTracker.Api.Services;

namespace StudyTracker.Api.Endpoints;

public static class ChatEndpoints
{
    public static void MapChatEndpoints(this IEndpointRouteBuilder app)
    {
        var group = app.MapGroup("/api/chat")
            .RequireAuthorization();

        group.MapPost("/conversations", CreateConversationAsync)
            .WithName("ChatCreateConversation");

        group.MapPost("/conversations/{id:guid}/messages", SendMessageAsync)
            .WithName("ChatSendMessage");

        group.MapGet("/conversations/{id:guid}/messages", GetMessagesAsync)
            .WithName("ChatGetMessages");
    }

    private static async Task<AppUser?> LoadApprovedUserAsync(
        HttpContext httpContext,
        StudyTrackerContext db,
        CancellationToken ct)
    {
        var sub = httpContext.User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (string.IsNullOrWhiteSpace(sub) || !int.TryParse(sub, out var userId))
        {
            return null;
        }

        var user = await db.Users.AsNoTracking().FirstOrDefaultAsync(u => u.Id == userId, ct);
        if (user == null || !string.Equals(user.Status, "Approved", StringComparison.OrdinalIgnoreCase))
        {
            return null;
        }

        return user;
    }

    private static async Task<IResult> CreateConversationAsync(
        CreateChatConversationRequest request,
        StudyTrackerContext db,
        HttpContext httpContext,
        CancellationToken ct)
    {
        var user = await LoadApprovedUserAsync(httpContext, db, ct);
        if (user == null)
        {
            return Problem(httpContext, StatusCodes.Status401Unauthorized, "Unauthorized", "User account is not approved or authenticated.");
        }

        string? title = request.Title?.Trim();

        if (request.LessonId.HasValue)
        {
            var lesson = await db.Lessons.AsNoTracking().FirstOrDefaultAsync(l => l.Id == request.LessonId.Value, ct);
            if (lesson == null)
            {
                return Problem(httpContext, StatusCodes.Status404NotFound, "Lesson not found", $"No lesson found with ID {request.LessonId.Value}.");
            }
            if (string.IsNullOrWhiteSpace(title))
            {
                title = $"Chat: {lesson.Title}";
            }
        }

        if (string.IsNullOrWhiteSpace(title))
        {
            title = "New Conversation";
        }

        var conversation = new ChatConversation
        {
            Id = Guid.NewGuid(),
            UserId = user.Id,
            LessonId = request.LessonId,
            Title = title.Length > 200 ? title[..200] : title,
            CreatedAt = DateTime.UtcNow,
            UpdatedAt = DateTime.UtcNow
        };

        db.ChatConversations.Add(conversation);
        await db.SaveChangesAsync(ct);

        return Results.Created(
            $"/api/chat/conversations/{conversation.Id}",
            new ChatConversationDto(
                conversation.Id,
                conversation.UserId,
                conversation.LessonId,
                conversation.Title,
                conversation.CreatedAt,
                conversation.UpdatedAt
            ));
    }

    private static async Task<IResult> SendMessageAsync(
        Guid id,
        SendChatMessageRequest request,
        StudyTrackerContext db,
        LlamaApiClient llamaClient,
        BudgetGuardService budgetGuard,
        IOptions<LlamaApiOptions> llamaOptions,
        ILogger<LlamaApiClient> logger,
        HttpContext httpContext,
        CancellationToken ct)
    {
        var user = await LoadApprovedUserAsync(httpContext, db, ct);
        if (user == null)
        {
            return Problem(httpContext, StatusCodes.Status401Unauthorized, "Unauthorized", "User account is not approved or authenticated.");
        }

        if (string.IsNullOrWhiteSpace(request.Content))
        {
            return Problem(httpContext, StatusCodes.Status400BadRequest, "Bad Request", "Message content cannot be empty.");
        }

        var conversation = await db.ChatConversations
            .Include(c => c.Lesson)
            .FirstOrDefaultAsync(c => c.Id == id && c.UserId == user.Id, ct);

        if (conversation == null)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Conversation not found", $"Conversation {id} was not found.");
        }

        // Idempotency check: if clientRequestId already processed and responded to
        if (!string.IsNullOrWhiteSpace(request.ClientRequestId))
        {
            var existingUserMsg = await db.ChatMessages.AsNoTracking()
                .FirstOrDefaultAsync(m => m.ConversationId == id && m.ClientRequestId == request.ClientRequestId, ct);

            if (existingUserMsg != null)
            {
                var existingAssistantMsg = await db.ChatMessages.AsNoTracking()
                    .Where(m => m.ConversationId == id && m.Role == "assistant" && m.CreatedAt >= existingUserMsg.CreatedAt)
                    .OrderBy(m => m.CreatedAt)
                    .FirstOrDefaultAsync(ct);

                if (existingAssistantMsg != null)
                {
                    return Results.Ok(new ChatMessageDto(
                        existingAssistantMsg.Id,
                        existingAssistantMsg.ConversationId,
                        existingAssistantMsg.Role,
                        existingAssistantMsg.Content,
                        existingAssistantMsg.ClientRequestId,
                        existingAssistantMsg.PromptTokens,
                        existingAssistantMsg.CompletionTokens,
                        existingAssistantMsg.UsageEstimated,
                        existingAssistantMsg.EstimatedCostUsd,
                        existingAssistantMsg.LatencyMs,
                        existingAssistantMsg.CreatedAt
                    ));
                }
            }
        }

        // Budget Guard Check before calling model
        var (allowed, usage) = await budgetGuard.TryReserveRequestAsync(ct);
        if (!allowed)
        {
            return Problem(
                httpContext,
                StatusCodes.Status429TooManyRequests,
                "Daily AI Compute Cap Reached",
                $"Neuralascent's shared daily AI budget of ${usage.DailyCapUsd:F2}/day has been reached for today (UTC). The cap resets at midnight UTC. Please try again tomorrow.");
        }

        // Save User Message
        var userMsg = new ChatMessage
        {
            Id = Guid.NewGuid(),
            ConversationId = id,
            Role = "user",
            Content = request.Content.Trim(),
            ClientRequestId = request.ClientRequestId?.Trim(),
            CreatedAt = DateTime.UtcNow
        };
        db.ChatMessages.Add(userMsg);
        await db.SaveChangesAsync(ct);

        // Build prompt context
        var options = llamaOptions.Value;
        var maxContextChars = options.MaxContextCharacters > 0 ? options.MaxContextCharacters : 6000;
        var maxHistory = options.MaxHistoryMessages > 0 ? options.MaxHistoryMessages : 10;

        var systemPromptBuilder = new StringBuilder();
        systemPromptBuilder.AppendLine("You are the Neuralascent AI Learning Assistant, dedicated to helping the learner understand computer science, distributed systems, and software engineering concepts.");

        if (conversation.Lesson != null)
        {
            systemPromptBuilder.AppendLine("\n--- CURRENT LESSON MATERIAL ---");
            systemPromptBuilder.AppendLine($"Title: {conversation.Lesson.Title}");
            if (!string.IsNullOrWhiteSpace(conversation.Lesson.Description))
            {
                systemPromptBuilder.AppendLine($"Overview: {conversation.Lesson.Description}");
            }

            // Fetch any lesson notes for additional grounding
            var lessonNotes = await db.LessonNotes.AsNoTracking()
                .Where(n => n.LessonId == conversation.Lesson.Id)
                .OrderBy(n => n.OrderIndex)
                .Take(5)
                .Select(n => n.Content)
                .ToListAsync(ct);

            if (lessonNotes.Count > 0)
            {
                systemPromptBuilder.AppendLine("Key Notes:");
                foreach (var note in lessonNotes)
                {
                    systemPromptBuilder.AppendLine($"- {note}");
                }
            }

            systemPromptBuilder.AppendLine("--- END OF LESSON MATERIAL ---");
            systemPromptBuilder.AppendLine("Ground your responses in this lesson material whenever applicable. Be educational, encouraging, and clear.");
        }

        var systemPrompt = systemPromptBuilder.ToString();
        if (systemPrompt.Length > maxContextChars)
        {
            systemPrompt = systemPrompt[..maxContextChars] + "\n[Context Truncated]";
        }

        // Retrieve conversation history (excluding the user message we just added)
        var historyMessages = await db.ChatMessages.AsNoTracking()
            .Where(m => m.ConversationId == id && m.Id != userMsg.Id && (m.Role == "user" || m.Role == "assistant"))
            .OrderByDescending(m => m.CreatedAt)
            .Take(maxHistory)
            .OrderBy(m => m.CreatedAt)
            .ToListAsync(ct);

        var promptMessages = new List<ChatPromptMessage>
        {
            new("system", systemPrompt)
        };

        foreach (var hm in historyMessages)
        {
            promptMessages.Add(new(hm.Role, hm.Content));
        }

        promptMessages.Add(new("user", userMsg.Content));

        // Call Meta Llama API
        LlamaCompletionResult reply;
        try
        {
            reply = await llamaClient.GenerateCompletionAsync(promptMessages, ct);
        }
        catch (Exception ex)
        {
            logger.LogError(ex, "Failed to get completion from Llama API for conversation {ConversationId}", id);
            return Problem(httpContext, StatusCodes.Status502BadGateway, "AI Service Error", "Failed to communicate with the AI language service. Please try again in a few moments.");
        }

        // Save Assistant Message
        var assistantMsg = new ChatMessage
        {
            Id = Guid.NewGuid(),
            ConversationId = id,
            Role = "assistant",
            Content = reply.ReplyContent,
            PromptTokens = reply.PromptTokens,
            CompletionTokens = reply.CompletionTokens,
            UsageEstimated = reply.UsageEstimated,
            EstimatedCostUsd = reply.EstimatedCostUsd,
            LatencyMs = reply.LatencyMs,
            CreatedAt = DateTime.UtcNow
        };

        conversation.UpdatedAt = DateTime.UtcNow;
        db.ChatMessages.Add(assistantMsg);
        await db.SaveChangesAsync(ct);

        return Results.Ok(new ChatMessageDto(
            assistantMsg.Id,
            assistantMsg.ConversationId,
            assistantMsg.Role,
            assistantMsg.Content,
            assistantMsg.ClientRequestId,
            assistantMsg.PromptTokens,
            assistantMsg.CompletionTokens,
            assistantMsg.UsageEstimated,
            assistantMsg.EstimatedCostUsd,
            assistantMsg.LatencyMs,
            assistantMsg.CreatedAt
        ));
    }

    private static async Task<IResult> GetMessagesAsync(
        Guid id,
        StudyTrackerContext db,
        HttpContext httpContext,
        CancellationToken ct)
    {
        var user = await LoadApprovedUserAsync(httpContext, db, ct);
        if (user == null)
        {
            return Problem(httpContext, StatusCodes.Status401Unauthorized, "Unauthorized", "User account is not approved or authenticated.");
        }

        var conversation = await db.ChatConversations.AsNoTracking()
            .FirstOrDefaultAsync(c => c.Id == id && c.UserId == user.Id, ct);

        if (conversation == null)
        {
            return Problem(httpContext, StatusCodes.Status404NotFound, "Conversation not found", $"Conversation {id} was not found.");
        }

        var messages = await db.ChatMessages.AsNoTracking()
            .Where(m => m.ConversationId == id)
            .OrderBy(m => m.CreatedAt)
            .Select(m => new ChatMessageDto(
                m.Id,
                m.ConversationId,
                m.Role,
                m.Content,
                m.ClientRequestId,
                m.PromptTokens,
                m.CompletionTokens,
                m.UsageEstimated,
                m.EstimatedCostUsd,
                m.LatencyMs,
                m.CreatedAt
            ))
            .ToListAsync(ct);

        return Results.Ok(messages);
    }

    private static IResult Problem(HttpContext context, int statusCode, string title, string detail)
    {
        return Results.Json(
            new
            {
                type = "https://tools.ietf.org/html/rfc7231",
                title,
                status = statusCode,
                detail,
                instance = context.Request.Path.Value,
                traceId = context.TraceIdentifier
            },
            contentType: "application/problem+json",
            statusCode: statusCode);
    }
}
