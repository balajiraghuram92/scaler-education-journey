using System;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Options;
using StudyTracker.Api.Options;

namespace StudyTracker.Api.Services.Auth;

public class TotpSecretProtector
{
    private readonly byte[] _key;
    private const int NonceSizeBytes = 12;
    private const int TagSizeBytes = 16;

    public TotpSecretProtector(IOptions<AuthOptions> options, IHostEnvironment env)
    {
        var rawKeyStr = options.Value.TotpEncryptionKey;
        if (string.IsNullOrWhiteSpace(rawKeyStr))
        {
            if (env.IsProduction())
            {
                throw new InvalidOperationException("Production configuration error: Auth:TotpEncryptionKey must be set.");
            }

            // Local-dev-only convenience: a fresh random key each process start — never a fixed string.
            // Any TOTP secret encrypted before a dev restart becomes undecryptable; that is acceptable in dev.
            rawKeyStr = Convert.ToBase64String(RandomNumberGenerator.GetBytes(32));
            Console.WriteLine("WARNING: Auth:TotpEncryptionKey not configured — using an ephemeral random dev-only key. Set Auth__TotpEncryptionKey for any shared or persistent environment.");
        }

        try
        {
            var decoded = Convert.FromBase64String(rawKeyStr);
            if (decoded.Length == 32)
            {
                _key = decoded;
            }
            else
            {
                using var sha = SHA256.Create();
                _key = sha.ComputeHash(decoded);
            }
        }
        catch (FormatException)
        {
            using var sha = SHA256.Create();
            _key = sha.ComputeHash(Encoding.UTF8.GetBytes(rawKeyStr));
        }
    }

    public string Encrypt(byte[] rawSecret)
    {
        ArgumentNullException.ThrowIfNull(rawSecret);

        byte[] nonce = RandomNumberGenerator.GetBytes(NonceSizeBytes);
        byte[] ciphertext = new byte[rawSecret.Length];
        byte[] tag = new byte[TagSizeBytes];

        using var aesGcm = new AesGcm(_key, TagSizeBytes);
        aesGcm.Encrypt(nonce, rawSecret, ciphertext, tag);

        // payload = nonce (12 bytes) || ciphertext (variable) || tag (16 bytes)
        byte[] payload = new byte[NonceSizeBytes + ciphertext.Length + TagSizeBytes];
        Buffer.BlockCopy(nonce, 0, payload, 0, NonceSizeBytes);
        Buffer.BlockCopy(ciphertext, 0, payload, NonceSizeBytes, ciphertext.Length);
        Buffer.BlockCopy(tag, 0, payload, NonceSizeBytes + ciphertext.Length, TagSizeBytes);

        return Convert.ToBase64String(payload);
    }

    public byte[] Decrypt(string encrypted)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(encrypted);

        byte[] payload = Convert.FromBase64String(encrypted);
        if (payload.Length < NonceSizeBytes + TagSizeBytes)
        {
            throw new CryptographicException("Encrypted TOTP secret payload is malformed or too short.");
        }

        int ciphertextLength = payload.Length - NonceSizeBytes - TagSizeBytes;

        byte[] nonce = new byte[NonceSizeBytes];
        byte[] ciphertext = new byte[ciphertextLength];
        byte[] tag = new byte[TagSizeBytes];

        Buffer.BlockCopy(payload, 0, nonce, 0, NonceSizeBytes);
        Buffer.BlockCopy(payload, NonceSizeBytes, ciphertext, 0, ciphertextLength);
        Buffer.BlockCopy(payload, NonceSizeBytes + ciphertextLength, tag, 0, TagSizeBytes);

        byte[] plaintext = new byte[ciphertextLength];
        using var aesGcm = new AesGcm(_key, TagSizeBytes);
        aesGcm.Decrypt(nonce, ciphertext, tag, plaintext);

        return plaintext;
    }
}
