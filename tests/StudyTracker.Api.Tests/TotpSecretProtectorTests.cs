using System;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Options;
using StudyTracker.Api.Services.Auth;
using Xunit;

namespace StudyTracker.Api.Tests;

public class TotpSecretProtectorTests
{
    private readonly TotpSecretProtector _protector;

    public TotpSecretProtectorTests()
    {
        // 32-byte key base64 encoded
        var rawKey = RandomNumberGenerator.GetBytes(32);
        var base64Key = Convert.ToBase64String(rawKey);

        var options = Options.Create(new AuthOptions
        {
            TotpEncryptionKey = base64Key
        });

        _protector = new TotpSecretProtector(options);
    }

    [Fact]
    public void EncryptAndDecrypt_RoundTrip_PreservesExactSecretBytes()
    {
        var secret = RandomNumberGenerator.GetBytes(20);
        var encrypted = _protector.Encrypt(secret);

        Assert.False(string.IsNullOrWhiteSpace(encrypted));

        var decrypted = _protector.Decrypt(encrypted);

        Assert.Equal(secret, decrypted);
    }

    [Fact]
    public void Encrypt_ProducesDifferentCiphertexts_DueToRandomNonce()
    {
        var secret = RandomNumberGenerator.GetBytes(20);
        var ciphertext1 = _protector.Encrypt(secret);
        var ciphertext2 = _protector.Encrypt(secret);

        Assert.NotEqual(ciphertext1, ciphertext2);

        // Both decrypt to the same secret
        Assert.Equal(secret, _protector.Decrypt(ciphertext1));
        Assert.Equal(secret, _protector.Decrypt(ciphertext2));
    }

    [Fact]
    public void Decrypt_TamperedPayload_ThrowsCryptographicException()
    {
        var secret = RandomNumberGenerator.GetBytes(20);
        var encrypted = _protector.Encrypt(secret);

        var payload = Convert.FromBase64String(encrypted);
        // Tamper with one byte in the ciphertext portion
        payload[^1] ^= 0xFF;
        var tampered = Convert.ToBase64String(payload);

        Assert.Throws<CryptographicException>(() => _protector.Decrypt(tampered));
    }

    [Theory]
    [InlineData("")]
    [InlineData(" ")]
    [InlineData(null)]
    public void Decrypt_EmptyOrNull_ThrowsArgumentException(string? invalidInput)
    {
        Assert.ThrowsAny<ArgumentException>(() => _protector.Decrypt(invalidInput!));
    }

    [Fact]
    public void Decrypt_TruncatedPayload_ThrowsCryptographicException()
    {
        // Nonce is 12 bytes and tag is 16 bytes = 28 bytes minimum. Anything shorter must fail.
        var shortPayload = Convert.ToBase64String(new byte[20]);
        Assert.Throws<CryptographicException>(() => _protector.Decrypt(shortPayload));
    }
}
