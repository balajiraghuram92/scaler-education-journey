using System;
using System.Net;
using System.Net.Mail;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Models;
using StudyTracker.Api.Options;

namespace StudyTracker.Api.Services.Email;

public class SmtpEmailNotificationService : IEmailNotificationService
{
    private readonly string _host;
    private readonly int _port;
    private readonly string _username;
    private readonly string _password;
    private readonly bool _enableSsl;
    private readonly string _fromEmail;
    private readonly string _fromName;
    private readonly string _frontendUrl;
    private readonly string? _adminNotificationEmail;
    private readonly bool _isConfigured;
    private readonly ILogger<SmtpEmailNotificationService> _logger;

    public SmtpEmailNotificationService(
        IOptions<EmailOptions> emailOptions,
        IOptions<SmtpOptions>? smtpOptions,
        ILogger<SmtpEmailNotificationService> logger)
    {
        _logger = logger;

        var email = emailOptions?.Value ?? new EmailOptions();
        var smtp = smtpOptions?.Value;

        _host = !string.IsNullOrWhiteSpace(email.SmtpHost)
            ? email.SmtpHost
            : (smtp?.Host ?? string.Empty);

        _port = email.SmtpPort > 0 ? email.SmtpPort : (smtp?.Port ?? 587);

        _username = !string.IsNullOrWhiteSpace(email.SmtpUsername)
            ? email.SmtpUsername
            : (smtp?.Username ?? string.Empty);

        _password = !string.IsNullOrWhiteSpace(email.SmtpPassword)
            ? email.SmtpPassword
            : (smtp?.Password ?? string.Empty);

        _enableSsl = email.UseSsl;

        _fromEmail = !string.IsNullOrWhiteSpace(email.FromAddress)
            ? email.FromAddress
            : (!string.IsNullOrWhiteSpace(smtp?.FromEmail) ? smtp.FromEmail : "noreply@neuralascent.top");

        _fromName = !string.IsNullOrWhiteSpace(email.FromDisplayName)
            ? email.FromDisplayName
            : (!string.IsNullOrWhiteSpace(smtp?.FromName) ? smtp.FromName : "Neuralascent");

        _frontendUrl = smtp?.FrontendUrl ?? "https://neuralascent.top";
        _adminNotificationEmail = smtp?.AdminNotificationEmail;

        _isConfigured = !string.IsNullOrWhiteSpace(_host) && !string.IsNullOrWhiteSpace(_fromEmail);
    }

    public async Task SendAdminNewUserAlertAsync(AppUser newUser, CancellationToken ct = default)
    {
        var recipient = !string.IsNullOrWhiteSpace(_adminNotificationEmail)
            ? _adminNotificationEmail
            : _fromEmail;

        var subject = $"[Neuralascent] New User Registration Pending Approval: {newUser.Email}";
        var body = $@"
            <h2>New User Registration Pending Approval</h2>
            <p>A new user has registered on Neuralascent and is awaiting your review:</p>
            <ul>
                <li><strong>Email:</strong> {WebUtility.HtmlEncode(newUser.Email)}</li>
                <li><strong>Name:</strong> {WebUtility.HtmlEncode(newUser.DisplayName ?? "Not provided")}</li>
                <li><strong>Registered At:</strong> {newUser.CreatedAt:yyyy-MM-dd HH:mm:ss} UTC</li>
            </ul>
            <p>Please log in to the <a href=""{_frontendUrl}/admin/users"">Admin Dashboard</a> to approve or reject this request.</p>";

        await SendEmailSafeAsync(recipient, subject, body, ct);
    }

    public async Task SendUserPendingConfirmationAsync(AppUser newUser, CancellationToken ct = default)
    {
        var subject = "[Neuralascent] Registration Received - Pending Approval";
        var body = $@"
            <h2>Welcome to Neuralascent</h2>
            <p>Hello {WebUtility.HtmlEncode(newUser.DisplayName ?? newUser.Email)},</p>
            <p>Thank you for registering on Neuralascent. Your account request has been received and is currently under administrative review.</p>
            <p>You will receive another email notification as soon as an administrator reviews and approves your account.</p>
            <p>Warm regards,<br/>The Neuralascent Team</p>";

        await SendEmailSafeAsync(newUser.Email, subject, body, ct);
    }

    public async Task SendUserApprovedNoticeAsync(AppUser user, CancellationToken ct = default)
    {
        var loginUrl = $"{_frontendUrl}/login";
        var subject = "[Neuralascent] Your Account Has Been Approved!";
        var body = $@"
            <h2>Welcome to Neuralascent — Access Approved</h2>
            <p>Hello {WebUtility.HtmlEncode(user.DisplayName ?? user.Email)},</p>
            <p>Great news! Your Neuralascent account registration has been approved by an administrator.</p>
            <p>You may now sign in to explore the curriculum, interactive reading rooms, and knowledge atlas:</p>
            <p><a href=""{loginUrl}"" style=""display:inline-block;padding:10px 20px;background-color:#2C5E55;color:#ffffff;text-decoration:none;border-radius:6px;font-weight:600;"">Sign In to Neuralascent</a></p>
            <p>Or visit: <a href=""{loginUrl}"">{loginUrl}</a></p>
            <p style=""margin-top:20px;padding:12px;background:#f4efe6;border-left:4px solid #2C5E55;font-size:0.9em;color:#4A4843;"">
                <strong>Sustainability note:</strong> Neuralascent runs on a single small host with a shared daily AI compute budget ($2.00/day hard cap). Please use the lesson assistant thoughtfully so everyone has access.
            </p>
            <p>Warm regards,<br/>The Neuralascent Team</p>";

        await SendEmailSafeAsync(user.Email, subject, body, ct);
    }

    public async Task SendUserRejectedNoticeAsync(AppUser user, string? reason, CancellationToken ct = default)
    {
        var subject = "[Neuralascent] Registration Status Update";
        var reasonHtml = !string.IsNullOrWhiteSpace(reason)
            ? $"<p><strong>Reason provided:</strong> {WebUtility.HtmlEncode(reason)}</p>"
            : string.Empty;

        var body = $@"
            <h2>Registration Status Update</h2>
            <p>Hello {WebUtility.HtmlEncode(user.DisplayName ?? user.Email)},</p>
            <p>Thank you for your interest in Neuralascent. After review, your registration request could not be approved at this time.</p>
            {reasonHtml}
            <p>If you believe this decision was made in error, please contact support.</p>
            <p>Warm regards,<br/>The Neuralascent Team</p>";

        await SendEmailSafeAsync(user.Email, subject, body, ct);
    }

    private async Task SendEmailSafeAsync(string toEmail, string subject, string htmlBody, CancellationToken ct)
    {
        if (string.IsNullOrWhiteSpace(toEmail))
        {
            _logger.LogWarning("Skipping email dispatch: recipient address is empty. Subject: {Subject}", subject);
            return;
        }

        if (!_isConfigured)
        {
            _logger.LogInformation("[Dev Email Mock] SMTP not configured. Would send to '{To}': Subject: '{Subject}'", toEmail, subject);
            return;
        }

        try
        {
            using var client = new SmtpClient(_host, _port)
            {
                EnableSsl = _enableSsl
            };

            if (!string.IsNullOrWhiteSpace(_username))
            {
                client.Credentials = new NetworkCredential(_username, _password);
            }

            using var message = new MailMessage
            {
                From = new MailAddress(_fromEmail, _fromName),
                Subject = subject,
                Body = htmlBody,
                IsBodyHtml = true
            };

            message.To.Add(toEmail);

            await client.SendMailAsync(message, ct);
            _logger.LogInformation("Successfully sent email '{Subject}' to '{Recipient}' via {Host}:{Port}", subject, toEmail, _host, _port);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Failed to send email '{Subject}' to '{Recipient}' via SMTP host {Host}:{Port}", subject, toEmail, _host, _port);
        }
    }
}
