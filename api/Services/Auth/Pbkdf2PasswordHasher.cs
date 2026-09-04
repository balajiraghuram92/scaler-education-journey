using System;
using System.Security.Cryptography;

namespace StudyTracker.Api.Services.Auth;

public class Pbkdf2PasswordHasher : IPasswordHasher
{
    public const int DefaultIterations = 210_000;
    public const int SaltSizeBytes = 16;
    public const int HashSizeBytes = 32;

    public static string Hash(string password, out string salt, out int iterations)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(password);

        byte[] saltBytes = RandomNumberGenerator.GetBytes(SaltSizeBytes);
        iterations = DefaultIterations;

        byte[] hashBytes = Rfc2898DeriveBytes.Pbkdf2(
            password: password,
            salt: saltBytes,
            iterations: iterations,
            hashAlgorithm: HashAlgorithmName.SHA256,
            outputLength: HashSizeBytes);

        salt = Convert.ToBase64String(saltBytes);
        return Convert.ToBase64String(hashBytes);
    }

    public static bool Verify(string password, string storedHash, string storedSalt, int iterations)
    {
        if (string.IsNullOrWhiteSpace(password) || string.IsNullOrWhiteSpace(storedHash) || string.IsNullOrWhiteSpace(storedSalt))
        {
            return false;
        }

        try
        {
            byte[] saltBytes = Convert.FromBase64String(storedSalt);
            byte[] expectedHashBytes = Convert.FromBase64String(storedHash);

            byte[] actualHashBytes = Rfc2898DeriveBytes.Pbkdf2(
                password: password,
                salt: saltBytes,
                iterations: iterations > 0 ? iterations : DefaultIterations,
                hashAlgorithm: HashAlgorithmName.SHA256,
                outputLength: expectedHashBytes.Length);

            return CryptographicOperations.FixedTimeEquals(actualHashBytes, expectedHashBytes);
        }
        catch (FormatException)
        {
            return false;
        }
    }

    public string HashPassword(string password, out string salt, out int iterations)
    {
        return Hash(password, out salt, out iterations);
    }

    public bool VerifyPassword(string password, string storedHash, string storedSalt, int iterations)
    {
        return Verify(password, storedHash, storedSalt, iterations);
    }
}
