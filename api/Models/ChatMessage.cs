using System;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace StudyTracker.Api.Models;

[Table("chat_messages")]
public class ChatMessage
{
    [Key]
    [Column("id")]
    public Guid Id { get; set; } = Guid.NewGuid();

    [Column("conversation_id")]
    public Guid ConversationId { get; set; }

    [JsonIgnore]
    [ForeignKey(nameof(ConversationId))]
    public ChatConversation? Conversation { get; set; }

    [Required]
    [MaxLength(20)]
    [Column("role")]
    public string Role { get; set; } = "user"; // "system", "user", "assistant"

    [Required]
    [Column("content")]
    public string Content { get; set; } = string.Empty;

    [MaxLength(64)]
    [Column("client_request_id")]
    public string? ClientRequestId { get; set; }

    [Column("prompt_tokens")]
    public int? PromptTokens { get; set; }

    [Column("completion_tokens")]
    public int? CompletionTokens { get; set; }

    [Column("usage_estimated")]
    public bool UsageEstimated { get; set; } = false;

    [Column("estimated_cost_usd", TypeName = "numeric(10,6)")]
    public decimal? EstimatedCostUsd { get; set; }

    [Column("latency_ms")]
    public int? LatencyMs { get; set; }

    [Column("error_message")]
    public string? ErrorMessage { get; set; }

    [Column("created_at")]
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}
