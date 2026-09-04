using System;
using System.Collections.Generic;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Microsoft.Extensions.Options;
using Microsoft.IdentityModel.Tokens;
using StudyTracker.Api.Models;
using StudyTracker.Api.Options;

namespace StudyTracker.Api.Services.Auth;

public class JwtTokenService : IJwtTokenService
{
    private readonly AuthOptions _options;

    public JwtTokenService(IOptions<AuthOptions> authOptions, IOptions<JwtOptions>? jwtOptions = null)
    {
        var auth = authOptions?.Value ?? new AuthOptions();
        var jwt = jwtOptions?.Value;

        if (string.IsNullOrWhiteSpace(auth.JwtSigningKey) && !string.IsNullOrWhiteSpace(jwt?.SecretKey))
        {
            auth.JwtSigningKey = jwt.SecretKey;
        }
        if (string.IsNullOrWhiteSpace(auth.JwtIssuer) && !string.IsNullOrWhiteSpace(jwt?.Issuer))
        {
            auth.JwtIssuer = jwt.Issuer;
        }
        if (string.IsNullOrWhiteSpace(auth.JwtAudience) && !string.IsNullOrWhiteSpace(jwt?.Audience))
        {
            auth.JwtAudience = jwt.Audience;
        }

        _options = auth;
    }

    public string GenerateToken(AppUser user)
    {
        if (string.IsNullOrWhiteSpace(_options.JwtSigningKey))
        {
            throw new InvalidOperationException("Auth:JwtSigningKey must be configured.");
        }

        var tokenHandler = new JwtSecurityTokenHandler();
        var key = Encoding.UTF8.GetBytes(_options.JwtSigningKey);

        var claims = new List<Claim>
        {
            new(ClaimTypes.NameIdentifier, user.Id.ToString()),
            new(ClaimTypes.Email, user.Email),
            new(ClaimTypes.Role, user.Role),
            new(ClaimTypes.Name, user.DisplayName ?? user.Email),
            new("status", user.Status)
        };

        var tokenDescriptor = new SecurityTokenDescriptor
        {
            Subject = new ClaimsIdentity(claims),
            Expires = GetExpiration(),
            Issuer = _options.JwtIssuer,
            Audience = _options.JwtAudience,
            SigningCredentials = new SigningCredentials(new SymmetricSecurityKey(key), SecurityAlgorithms.HmacSha256Signature)
        };

        var token = tokenHandler.CreateToken(tokenDescriptor);
        return tokenHandler.WriteToken(token);
    }

    public DateTime GetExpiration()
    {
        var minutes = _options.JwtExpiryMinutes > 0 ? _options.JwtExpiryMinutes : 720;
        return DateTime.UtcNow.AddMinutes(minutes);
    }
}
