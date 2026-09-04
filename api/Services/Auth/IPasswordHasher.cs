namespace StudyTracker.Api.Services.Auth;

public interface IPasswordHasher
{
    string HashPassword(string password, out string salt, out int iterations);
    bool VerifyPassword(string password, string storedHash, string storedSalt, int iterations);
}
