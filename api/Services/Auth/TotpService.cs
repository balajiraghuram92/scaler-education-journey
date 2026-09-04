using System;
using System.Security.Cryptography;
using System.Text;

namespace StudyTracker.Api.Services.Auth;

public interface ITotpService
{
    byte[] GenerateSecret();
    string ToBase32(byte[] secret);
    string BuildOtpAuthUri(string base32Secret, string email);
    long CurrentCounter();
    string ComputeCode(byte[] secret, long counter);
    bool TryVerify(byte[] secret, string code, long? lastAcceptedCounter, out long acceptedCounter);
}

public class TotpService : ITotpService
{
    private const int SecretSizeBytes = 20; // 160 bits
    private const int PeriodSeconds = 30;
    private static readonly char[] Base32Chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567".ToCharArray();

    public byte[] GenerateSecret()
    {
        return RandomNumberGenerator.GetBytes(SecretSizeBytes);
    }

    public string ToBase32(byte[] secret)
    {
        if (secret == null || secret.Length == 0)
        {
            return string.Empty;
        }

        var sb = new StringBuilder((secret.Length * 8 + 4) / 5);
        int buffer = 0;
        int bitsLeft = 0;

        foreach (byte b in secret)
        {
            buffer = (buffer << 8) | b;
            bitsLeft += 8;
            while (bitsLeft >= 5)
            {
                bitsLeft -= 5;
                sb.Append(Base32Chars[(buffer >> bitsLeft) & 0x1F]);
            }
        }

        if (bitsLeft > 0)
        {
            sb.Append(Base32Chars[(buffer << (5 - bitsLeft)) & 0x1F]);
        }

        return sb.ToString();
    }

    public string BuildOtpAuthUri(string base32Secret, string email)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(base32Secret);
        ArgumentException.ThrowIfNullOrWhiteSpace(email);

        var encodedEmail = Uri.EscapeDataString(email.Trim());
        return $"otpauth://totp/Neuralascent:{encodedEmail}?secret={base32Secret}&issuer=Neuralascent&algorithm=SHA1&digits=6&period={PeriodSeconds}";
    }

    public long CurrentCounter()
    {
        return DateTimeOffset.UtcNow.ToUnixTimeSeconds() / PeriodSeconds;
    }

    public string ComputeCode(byte[] secret, long counter)
    {
        ArgumentNullException.ThrowIfNull(secret);

        byte[] counterBytes = BitConverter.GetBytes(counter);
        if (BitConverter.IsLittleEndian)
        {
            Array.Reverse(counterBytes);
        }

        using var hmac = new HMACSHA1(secret);
        byte[] hash = hmac.ComputeHash(counterBytes);

        // Dynamic truncation per RFC 4226 Section 5.3
        int offset = hash[^1] & 0x0F;
        int binary = ((hash[offset] & 0x7F) << 24)
                   | ((hash[offset + 1] & 0xFF) << 16)
                   | ((hash[offset + 2] & 0xFF) << 8)
                   | (hash[offset + 3] & 0xFF);

        int codeInt = binary % 1_000_000;
        return codeInt.ToString("D6");
    }

    public bool TryVerify(byte[] secret, string code, long? lastAcceptedCounter, out long acceptedCounter)
    {
        acceptedCounter = 0;
        if (secret == null || string.IsNullOrWhiteSpace(code))
        {
            return false;
        }

        var trimmedCode = code.Trim();
        if (trimmedCode.Length != 6 || !int.TryParse(trimmedCode, out _))
        {
            return false;
        }

        long current = CurrentCounter();
        long[] candidateSteps = [current - 1, current, current + 1];

        foreach (var step in candidateSteps)
        {
            // Replay protection: reject if counter was already used
            if (lastAcceptedCounter.HasValue && step <= lastAcceptedCounter.Value)
            {
                continue;
            }

            var expectedCode = ComputeCode(secret, step);
            if (CryptographicOperations.FixedTimeEquals(
                Encoding.UTF8.GetBytes(expectedCode),
                Encoding.UTF8.GetBytes(trimmedCode)))
            {
                acceptedCounter = step;
                return true;
            }
        }

        return false;
    }
}
