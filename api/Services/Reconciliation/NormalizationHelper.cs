using System;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;

namespace StudyTracker.Api.Services.Reconciliation;

public static class NormalizationHelper
{
    public static string NormalizeText(string? input)
    {
        if (string.IsNullOrWhiteSpace(input)) return string.Empty;
        var normalized = input.Trim().ToLowerInvariant();
        normalized = Regex.Replace(normalized, @"\s+", " ");
        // Strip common punctuation differences
        normalized = Regex.Replace(normalized, @"[^\w\s-]", "");
        return normalized.Trim();
    }

    public static string GenerateSlug(string text)
    {
        if (string.IsNullOrWhiteSpace(text)) return string.Empty;
        var slug = text.ToLowerInvariant().Trim();
        slug = Regex.Replace(slug, @"[^a-z0-9\s-]", "");
        slug = Regex.Replace(slug, @"\s+", "-");
        slug = Regex.Replace(slug, @"-+", "-");
        return slug.Trim('-');
    }

    public static string ComputeSha256Checksum(string input)
    {
        using var sha256 = SHA256.Create();
        var bytes = Encoding.UTF8.GetBytes(input);
        var hash = sha256.ComputeHash(bytes);
        return Convert.ToHexString(hash).ToLowerInvariant();
    }
}
