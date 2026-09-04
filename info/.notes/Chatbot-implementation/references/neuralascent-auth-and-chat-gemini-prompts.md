# Neuralascent — Auth, Approval, TOTP & AI-Chat Infra: Gemini Execution Package

**Status:** implemented; two critical fixes required before push (see "Code Review Findings" at the end). **Last updated:** 2026-09-04 (adds Code Review Findings — hardcoded fallback secrets in `Program.cs` and `TotpSecretProtector.cs`).

Run these against the `scaler-education-journey` repo, in order, verifying each one builds/migrates/runs before starting the next:

1. **Part A** — Auth & approval foundation (signup, admin-dashboard approve/reject + email, secure cookie JWT login)
2. **Part A — Corrections** — six fixes to apply *before* Part A is implemented (not after) — paste this immediately alongside Part A, not as a follow-up patch
3. **Part B** — Mandatory TOTP (Google Authenticator-compatible) second login factor, free, for every user including the admin
4. **Part C** — Meta Llama API chat, gated behind login, with a hard $2.00/day spend cap

Design decisions locked in for this package (see [[neuralascent-ai-vertical-vs-ai-integration]] in Claude's memory for the full rationale trail):
- Self-serve email signup stays; only the **approve/reject decision and its notification email** happen via the admin dashboard.
- First admin is bootstrapped via a `--seed-admin` CLI command (never a hardcoded/default password, in any environment).
- TOTP, not SMS/email OTP or a paid MFA service — it's free (pure shared-secret + time math, no third party), and applies to *every* user, admin included.
- `/api/auth/*` stays behind the same `x-api-key` gate as every other `/api/*` route — nginx already injects the real key server-side for the whole `/api` path ([app/Dockerfile](../../../../api), `app/docker-entrypoint-custom.sh`), so no frontend or middleware change was needed there.
- Chat is Meta Llama API, hard-blocked at $2.00/day spend (plus an independent request-count backstop so the cap can't silently fail if token-usage parsing ever breaks).

---

## Part A — Auth foundation (signup, approval, JWT login, admin)

```
You are making infrastructure changes to the Neuralascent repo (React frontend in `app/`, ASP.NET Core 8 minimal-API backend in `api/`, PostgreSQL via EF Core/Npgsql). This adds email signup with admin approval, secure cookie-based JWT login, and an admin dashboard for approving/rejecting users. Read every file listed below before editing anything, and match each file's existing style exactly (namespaces, `[Column]`/`[Table]` snake_case mapping, sealed records for DTOs, minimal-API `MapGroup` style with a `Problem(...)` helper, the frontend's `ApiError`/`apiClient` wrapper).

Read first: `api/Program.cs`, `api/Data/StudyTrackerContext.cs`, `api/Models/LessonNote.cs`, `api/Endpoints/ExerciseEndpoints.cs`, `api/Options/ExerciseExecutionOptions.cs`, `api/StudyTracker.Api.csproj`, `app/src/api/client.js`, `app/src/App.jsx`, `app/src/main.jsx`.

## New NuGet package (the one exception to "no new packages")
Add `Microsoft.AspNetCore.Authentication.JwtBearer` to `api/StudyTracker.Api.csproj`, version-pinned to match the other `Microsoft.*` packages already there (currently `8.0.28`/`8.0.0` range — use the latest `8.0.x` patch). Do not add any other package. Password hashing uses the built-in `System.Security.Cryptography.Rfc2898DeriveBytes.Pbkdf2` static method — no package needed. Email uses the built-in `System.Net.Mail.SmtpClient` — no package needed, and stays provider-agnostic (works against Gmail SMTP, AWS SES SMTP, SendGrid SMTP relay, Resend SMTP, etc. — do not hardcode a specific vendor's SDK).

## 1. `api/Models/AppUser.cs` (new)
Same attribute style as `api/Models/LessonNote.cs`. Table `app_users`.
- `Id` (int, PK, column `id`)
- `Email` (string, MaxLength 320, required, column `email`) — unique index, configure in `OnModelCreating`
- `PasswordHash` (string, column `password_hash`)
- `PasswordSalt` (string, column `password_salt`)
- `PasswordIterations` (int, column `password_iterations`)
- `Role` (string, MaxLength 20, default `"User"`, column `role`) — values `"User"` | `"Admin"`
- `Status` (string, MaxLength 30, default `"PendingApproval"`, column `status`) — values `"PendingApproval"` | `"Approved"` | `"Rejected"` | `"Disabled"`
- `DisplayName` (string?, MaxLength 120, column `display_name`)
- `CreatedAt` (DateTime, UTC now default, column `created_at`)
- `DecidedAt` (DateTime?, column `decided_at`)
- `DecidedByUserId` (int?, column `decided_by_user_id`) + `[JsonIgnore] [ForeignKey(nameof(DecidedByUserId))] public AppUser? DecidedByUser { get; set; }`
- `LastLoginAt` (DateTime?, column `last_login_at`)

## 2. `api/Models/AuthDtos.cs` (new)
Namespace `StudyTracker.Api.Models`, sealed records:
```csharp
public sealed record SignupRequest(string Email, string Password, string? DisplayName);
public sealed record LoginRequest(string Email, string Password);
public sealed record RejectUserRequest(string? Reason);
public sealed record UserDto(int Id, string Email, string? DisplayName, string Role, string Status, DateTime CreatedAt, DateTime? LastLoginAt);
```

## 3. `api/Options/AuthOptions.cs` (new)
Same pattern as `ExerciseExecutionOptions.cs`. `SectionName = "Auth"`.
- `string JwtSigningKey { get; set; } = string.Empty;` — required in production, sourced from env only, never a default in `appsettings.json`
- `string JwtIssuer { get; set; } = "neuralascent";`
- `string JwtAudience { get; set; } = "neuralascent-app";`
- `int JwtExpiryMinutes { get; set; } = 720;` (12h — see Part A Correction 5 below, which supersedes any "7 days" language you may see elsewhere)
- `string CookieName { get; set; } = "na_auth";`
- `int MinPasswordLength { get; set; } = 10;`

## 4. `api/Options/EmailOptions.cs` (new)
`SectionName = "Email"`.
- `string SmtpHost { get; set; } = string.Empty;`
- `int SmtpPort { get; set; } = 587;`
- `string SmtpUsername { get; set; } = string.Empty;`
- `string SmtpPassword { get; set; } = string.Empty;` — env-sourced secret, never in appsettings.json
- `bool UseSsl { get; set; } = true;`
- `string FromAddress { get; set; } = "noreply@neuralascent.top";`
- `string FromDisplayName { get; set; } = "Neuralascent";`

## 5. `api/Services/PasswordHasher.cs` (new)
Static class, namespace `StudyTracker.Api.Services`. Constants: `SaltSizeBytes = 16`, `KeyLengthBytes = 32`, `DefaultIterations = 210_000` (OWASP 2023 PBKDF2-SHA256 recommendation).
- `static (string Hash, string Salt, int Iterations) HashPassword(string password)` — generates a random salt via `RandomNumberGenerator.GetBytes(SaltSizeBytes)`, derives with `Rfc2898DeriveBytes.Pbkdf2(password, salt, DefaultIterations, HashAlgorithmName.SHA256, KeyLengthBytes)`, returns both as Base64 plus the iteration count used.
- `static bool VerifyPassword(string password, string storedHashBase64, string storedSaltBase64, int iterations)` — recomputes with the *stored* iteration count (not the constant, so future increases don't break old hashes) and compares with `CryptographicOperations.FixedTimeEquals`.

## 6. `api/Services/JwtTokenService.cs` (new)
Namespace `StudyTracker.Api.Services`, constructor takes `IOptions<AuthOptions>`.
- `string IssueToken(AppUser user)` — builds a `JwtSecurityToken` (via `System.IdentityModel.Tokens.Jwt`, pulled in transitively by the JwtBearer package) with claims: `sub`=user id, `email`, `role`=user.Role, signed with `SymmetricSecurityKey` from `AuthOptions.JwtSigningKey` (HMAC-SHA256), issuer/audience/expiry from options. Returns the serialized token string.

## 7. `api/Services/EmailSender.cs` (new)
Namespace `StudyTracker.Api.Services`. Interface `IEmailSender` with `Task SendApprovalDecisionEmailAsync(string toEmail, bool approved, string? reason, CancellationToken ct)`. Implementation `SmtpEmailSender` (constructor takes `IOptions<EmailOptions>`, `ILogger<SmtpEmailSender>`) uses `System.Net.Mail.SmtpClient` to send a short plain-text email:
- If approved: subject "Your Neuralascent account is approved", body confirms they can log in now, and **must include this exact line**: "Note: AI chat usage is capped at $2.00 per day across all users to keep this sustainable — if the daily cap is reached, please try again after it resets at 00:00 UTC."
- If rejected: subject "Your Neuralascent account request", body says the request was not approved, includes `reason` if provided, no cap note.
- Catch and log (`LogError`) any `SmtpException` rather than letting it bubble up and fail the approve/reject API call — the approval decision must still succeed and persist even if the email fails to send. Do not throw from this method.

## 8. `api/Endpoints/AuthEndpoints.cs` (new)
Same structure as `api/Endpoints/ExerciseEndpoints.cs` (`MapGroup("/api/auth")`, `Problem(...)` helper, `.WithName(...)`).
- `POST /api/auth/signup` → validate email format and `Password.Length >= AuthOptions.MinPasswordLength` (400 if not), check `db.Users.AnyAsync(u => u.Email == email)` — if it already exists, still return the same 201-style generic success response (do not reveal whether the email is taken — enumeration protection) but don't create a duplicate row. Otherwise hash the password via `PasswordHasher`, create with `Status = "PendingApproval"`, `Role = "User"`, save, return `Results.Ok(new { message = "Thanks for signing up. An administrator will review your request." })`.
- `POST /api/auth/login` → look up by email; if not found or `PasswordHasher.VerifyPassword` fails, return 401 with a generic "Invalid email or password." (same message for both cases — don't leak which). If found and password correct but `Status != "Approved"`, return 403 with a message reflecting the actual status (`"Your account is awaiting approval."` / `"Your account request was not approved."` / `"Your account has been disabled."`). **See Part B below — once Part B is implemented, this endpoint's success path changes from "set the cookie" to "issue an MFA challenge"; implement Part A's version first (cookie issued directly here), then let Part B's edit supersede it.**
- `POST /api/auth/logout` → `context.Response.Cookies.Delete(authOptions.CookieName)`, return `Results.Ok()`.
- `GET /api/auth/me` → `.RequireAuthorization()`. Read `sub` claim for user id, load fresh from DB (not from stale claims — status may have changed since the token was issued), 401 if the user no longer exists, else return `Results.Ok(new UserDto(...))`.

## 9. `api/Endpoints/AdminEndpoints.cs` (new)
`MapGroup("/api/admin")` with `.RequireAuthorization("AdminOnly")` applied to the whole group.
- `GET /api/admin/users?status={status?}` → list users, optionally filtered by `Status`, ordered by `CreatedAt` descending, mapped to `UserDto`.
- `POST /api/admin/users/{id:int}/approve` → 404 if missing; if already `Approved`, return current state idempotently (don't re-send email); else set `Status = "Approved"`, `DecidedAt = DateTime.UtcNow`, `DecidedByUserId` = current admin's id (from `sub` claim), save, call `emailSender.SendApprovalDecisionEmailAsync(user.Email, true, null, ct)`, return `Results.Ok(new UserDto(...))`.
- `POST /api/admin/users/{id:int}/reject` (body: `RejectUserRequest`) → same idempotency/404 handling, sets `Status = "Rejected"`, sends the rejection email with `req.Reason`, returns `UserDto`.
- **See Part A Correction 5 below**: every handler in this file must reload the caller fresh from the DB and re-verify `Role == "Admin"` before proceeding — do not rely on `RequireAuthorization("AdminOnly")` (a JWT role claim) alone.

## 10. `api/Data/StudyTrackerContext.cs` — edit
- Add `public DbSet<AppUser> Users { get; set; } = null!;` under a new `// Auth DbSets` comment block, following the existing grouped-comment convention.
- In `OnModelCreating`, after the existing configuration (read the method fully first, add after it, don't reorder anything): configure a unique index on `AppUser.Email` (`modelBuilder.Entity<AppUser>().HasIndex(u => u.Email).IsUnique();`) and set the self-referencing `DecidedByUserId` FK to `DeleteBehavior.Restrict` (self-referencing cascades are rejected by EF/Npgsql migrations).

## 11. `api/Program.cs` — edit
- Add `using Microsoft.AspNetCore.Authentication.JwtBearer;`, `using Microsoft.IdentityModel.Tokens;`, `using System.Text;`.
- Register options (no `.ValidateOnStart()` — the app must still start in dev/CI without secrets configured; Production-only hard-fail is handled separately per Correction 2 below):
  ```csharp
  builder.Services.AddOptions<AuthOptions>().BindConfiguration(AuthOptions.SectionName);
  builder.Services.AddOptions<EmailOptions>().BindConfiguration(EmailOptions.SectionName);
  ```
- Register `builder.Services.AddSingleton<JwtTokenService>();`, `builder.Services.AddSingleton<IEmailSender, SmtpEmailSender>();`.
- Add authentication/authorization services (read current CORS policy block first and place this near it):
  ```csharp
  builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
      .AddJwtBearer(options =>
      {
          var authSection = builder.Configuration.GetSection(AuthOptions.SectionName);
          var signingKey = authSection["JwtSigningKey"] ?? string.Empty;
          options.TokenValidationParameters = new TokenValidationParameters
          {
              ValidateIssuerSigningKey = true,
              IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(signingKey.PadRight(32, '0'))),
              ValidateIssuer = true,
              ValidIssuer = authSection["JwtIssuer"] ?? "neuralascent",
              ValidateAudience = true,
              ValidAudience = authSection["JwtAudience"] ?? "neuralascent-app",
              ValidateLifetime = true
          };
          options.Events = new JwtBearerEvents
          {
              OnMessageReceived = context =>
              {
                  var cookieName = authSection["CookieName"] ?? "na_auth";
                  if (context.Request.Cookies.TryGetValue(cookieName, out var token))
                  {
                      context.Token = token;
                  }
                  return Task.CompletedTask;
              }
          };
      });
  builder.Services.AddAuthorization(options =>
  {
      options.AddPolicy("AdminOnly", policy => policy.RequireRole("Admin"));
  });
  ```
  (`.PadRight(32, '0')` is a local-dev-only minimum-length guard — see Correction 2, which makes this unreachable in Production.)
- In the CORS policy builder, add `.AllowCredentials()` to the existing `.WithOrigins(...).AllowAnyHeader().AllowAnyMethod()` chain (cookies require this).
- After `app.UseCors("AllowVite");` and before the existing API-key `app.Use(async (context, next) => { ... })` block, insert:
  ```csharp
  app.UseAuthentication();
  app.UseAuthorization();
  ```
  **Do not modify the API-key middleware itself or add any path exemption to it — see Correction 1.**
- Near `app.MapV2Endpoints(); app.MapImportEndpoints(); app.MapExerciseEndpoints();`, add `app.MapAuthEndpoints(); app.MapAdminEndpoints();`.
- Add a `--seed-admin` CLI mode — see Correction 3 for the exact required behavior (no default credentials, ever).

## 12. `api/appsettings.json` — edit
Add, as a sibling of `"ExerciseExecution"`, before `"AllowedHosts"` (no secrets — those come from env only):
```json
"Auth": {
  "JwtIssuer": "neuralascent",
  "JwtAudience": "neuralascent-app",
  "JwtExpiryMinutes": 720,
  "CookieName": "na_auth",
  "MinPasswordLength": 10
},
"Email": {
  "SmtpPort": 587,
  "UseSsl": true,
  "FromAddress": "noreply@neuralascent.top",
  "FromDisplayName": "Neuralascent"
},
```

## 13. `docker-compose.yml` — edit
See Correction 2 for the exact required env-var lines to add here (`Auth__JwtSigningKey`, `Smtp__Host`, `Smtp__User`, `Smtp__Pass`).

## 14. EF Core migration
After steps 1–10 compile:
```
dotnet ef migrations add AddUserAuth --project api --startup-project api
```
State this as an instruction; do not fabricate the generated migration file.

## 15. `app/src/api/client.js` — edit
In the `apiClient` function's `config` object (where `method`, `headers`, `body`, `signal` are set), add `credentials: 'include',` — required so the httpOnly auth cookie is sent on every request. Add an `auth` namespace to the exported `api` object, alongside `v2`/`legacy`:
```javascript
  auth: {
    signup: (email, password, displayName) => api.post('/api/auth/signup', { email, password, displayName }),
    login: (email, password) => api.post('/api/auth/login', { email, password }),
    logout: () => api.post('/api/auth/logout'),
    me: () => api.get('/api/auth/me'),
  },
  admin: {
    listUsers: (status) => apiClient(`/api/admin/users${status ? `?status=${encodeURIComponent(status)}` : ''}`),
    approveUser: (id) => api.post(`/api/admin/users/${id}/approve`),
    rejectUser: (id, reason) => api.post(`/api/admin/users/${id}/reject`, { reason }),
  },
```
(Note: Part B below changes what `login` returns — implement this shape first, then apply Part B's edit on top.)

## 16. `app/src/hooks/useAuth.jsx` (new)
A React context (`AuthContext`) + `AuthProvider` component + `useAuth()` hook. `AuthProvider` on mount calls `api.auth.me()`; on success stores the `UserDto` in state as `user`; on a 401 `ApiError`, sets `user = null` (not an error state — "not logged in" is expected, not exceptional). Exposes `{ user, loading, login(email, password), signup(email, password, displayName), logout(), refresh() }`. `login`/`signup`/`logout` call the corresponding `api.auth.*` method and then call `refresh()` (re-fetch `/api/auth/me`) to resync state.

## 17. `app/src/components/common/ProtectedRoute.jsx` (new)
Props: `{ children, requireAdmin }`. Uses `useAuth()`. While `loading`, render nothing (or the existing `LoadingState` from `StateViews.jsx`). If `!user`, `<Navigate to="/login" replace />`. If `requireAdmin && user.role !== 'Admin'`, `<Navigate to="/" replace />`. Otherwise render `children`.

## 18. `app/src/pages/Login.jsx`, `app/src/pages/Signup.jsx`, `app/src/pages/Admin.jsx` (+ matching `.css` files)
Match the function-component/hooks/plain-CSS-per-page conventions visible in `app/src/pages/ChapterReader.jsx` and reuse `LoadingState`/`ErrorState` from `app/src/components/common/StateViews.jsx` where reasonable.
- `Login.jsx`: email + password fields, calls `useAuth().login`, shows the server's error message inline on failure, redirects to `/` on success. **(Part B replaces this file's flow with a two-screen version — implement this simple version first.)**
- `Signup.jsx`: email + password + optional display name, calls `useAuth().signup`, shows the server's generic confirmation message (do not imply login happens automatically — it doesn't, approval is required first).
- `Admin.jsx`: on mount calls `api.admin.listUsers('PendingApproval')`, renders each pending user with Approve/Reject buttons (Reject opens a small inline text field for an optional reason), calls `api.admin.approveUser`/`rejectUser`, removes the row from the list on success.

## 19. `app/src/App.jsx` — edit
Add three new `<Route>` entries: `path="/login"` → `<Login />` (no `Layout` wrapper, it's a standalone auth screen), `path="/signup"` → `<Signup />` (same), `path="/admin"` → `<Layout><ProtectedRoute requireAdmin><Admin /></ProtectedRoute></Layout>`. Add the corresponding imports at the top alongside the existing page imports. Do not modify any existing route.

## 20. `app/src/main.jsx` — edit
Import `AuthProvider` from `./hooks/useAuth` and wrap `<App />` with it, inside `<StrictMode>`:
```jsx
<StrictMode>
  <AuthProvider>
    <App />
  </AuthProvider>
</StrictMode>
```

## Output format
Produce each new file in full. For each edited file, produce only the changed section with 3–5 lines of unchanged surrounding context. State the `dotnet ef migrations add` command as an instruction, not generated code.
```

---

## Part A — Corrections (apply alongside Part A, before implementation — this is not a later patch)

```
Apply these six corrections to the Part A plan above before implementing it. Re-read `api/Program.cs`, `docker-compose.yml`, `api/Data/StudyTrackerContext.cs`, and the three files named in point 1 first — do not implement from memory of the plan alone.

## 1. Do not touch `/api/auth`'s exposure to the API-key middleware — and do not add any x-api-key logic to the frontend
Read `app/Dockerfile`, `app/docker-entrypoint-custom.sh`, `app/default.conf.template`, `app/default.local.conf` first. Production nginx already injects the real `API_KEY` server-side into `proxy_set_header x-api-key "${API_KEY}"` for the *entire* `/api` location block — every path under `/api`, including the new `/api/auth/*` and `/api/admin/*` routes, already receives the correct key transparently. The secret never needs to reach the browser (`app/Dockerfile`'s own comment confirms this is intentional).
- **Do not** add any exemption for `/api/auth` (or anything else) to the API-key middleware in `api/Program.cs`. Leave that middleware exactly as it exists today, with zero path-based special cases added.
- **Do not** add `x-api-key` header logic to `app/src/api/client.js`. It is correct as-is on this point.
- If signup/login fail with 401 in local `docker compose up` testing, the fix is confirming `API_KEY` is set in your `.env` for that compose run — not modifying the middleware or the frontend.

## 2. Wire the JWT signing key (and SMTP credentials) into `docker-compose.yml` as required, fail-fast env vars
`docker-compose.yml` is currently missing from this plan's file list entirely. In the `api` service's `environment:` block, immediately after the existing `API_KEY: ${API_KEY:?API_KEY must be set}` line, add, following that exact same required-var convention:
```yaml
      Auth__JwtSigningKey: ${JWT_SIGNING_KEY:?JWT_SIGNING_KEY must be set (32+ random bytes, e.g. `openssl rand -base64 32`)}
      Smtp__Host: ${SMTP_HOST:?SMTP_HOST must be set}
      Smtp__User: ${SMTP_USER:?SMTP_USER must be set}
      Smtp__Pass: ${SMTP_PASS:?SMTP_PASS must be set}
```
Additionally, in `api/Program.cs`, in the same startup-verification block that already throws in Production when the database is unreachable (search for `IsProduction()` — read that whole block first), add an equivalent check: if `app.Environment.IsProduction()` and the configured JWT signing key is null/empty/shorter than 32 characters, throw and refuse to start. Do not silently pad or default the key in Production under any circumstance — padding is acceptable only as an explicit, clearly-commented local-dev convenience, never reachable when `IsProduction()` is true.

## 3. No default admin credentials, ever — and keep admin bootstrap out of `DbSeeder`/`--seed-reference-data`
Remove any `admin@neuralascent.local` / "secure default in non-production" fallback from the plan entirely. If `ADMIN_EMAIL` or `ADMIN_PASSWORD` is not supplied when the admin-bootstrap action runs, it must fail with a clear logged error and non-zero exit code — never fall back to a fixed or generated-but-undisclosed value baked into source.
- Do not fold admin creation into `DbSeeder.cs`'s normal path or trigger it from the existing `--seed-reference-data`/`--seed` CLI flag — that flag is for curriculum content and must never have a side effect on the one account that can approve users.
- Add a dedicated `--seed-admin` CLI mode in `api/Program.cs`, following the exact same shape (try/catch, logging, exit codes) as the existing `--migrate`/`--seed-reference-data`/`--reconcile-content` blocks in that file. It reads `ADMIN_EMAIL`/`ADMIN_PASSWORD` from configuration, upserts (by email) one `AppUser` with `Role = "Admin"`, `Status = "Approved"`, password hashed via the same `PasswordHasher` used everywhere else, and exits 1 with a clear message if either env var is missing.
- (Note: once Part B is implemented, the admin also completes TOTP enrollment on first login like every other user — no exemption.)

## 4. Generate the EF Core migration with the tool, not by hand
Do not hand-author a migration `.cs` file yourself. This repo's existing migrations (e.g. `api/Migrations/20260823183000_AddMigrationReconciliation.cs`) each ship with a paired `.Designer.cs` and an updated `api/Migrations/StudyTrackerContextModelSnapshot.cs` — a hand-written migration missing those will desync the EF model snapshot and likely break the next real migration. After `AppUser`, `StudyTrackerContext` changes, and DTOs compile, run:
```
dotnet ef migrations add AddUserAuth --project api --startup-project api
```
and let the tool generate all three files together.

## 5. Admin endpoints must recheck the caller's current DB state, not just trust the JWT's `Role` claim
`RequireRole("Admin")` alone only checks a claim that was baked into the token at login time. Combined with a multi-day token lifetime, a demoted or disabled admin keeps working admin access until their cookie expires. Fix two things:
- In `api/Endpoints/AdminEndpoints.cs`, before handling any admin action, reload the caller's `AppUser` fresh from the database (by the `sub`/`NameIdentifier` claim) and verify `Role == "Admin"` **and** `Status == "Approved"` against that fresh row — mirror whatever pattern `AuthEndpoints.GetMe` already uses for its own fresh-DB check, applied here too. Return 403 if either check fails, even though the JWT's own role claim still says `Admin`.
- Use 12 hours (`Auth:JwtExpiryMinutes = 720`) as the JWT lifetime, not 7 days — already reflected in the Part A file above; if any other value appears anywhere, this value wins.

## 6. Add rate limiting to `/api/auth/signup` and `/api/auth/login`
Neither endpoint has any rate limiting in the current plan, and these two are exactly what a signup-flood or credential-stuffing bot targets. In `api/Program.cs`, register ASP.NET Core's built-in rate limiter (`Microsoft.AspNetCore.RateLimiting` — ships in the .NET 8 shared framework, no new package needed):
```csharp
builder.Services.AddRateLimiter(options =>
{
    options.AddFixedWindowLimiter("AuthPolicy", opt =>
    {
        opt.PermitLimit = 10;
        opt.Window = TimeSpan.FromMinutes(15);
        opt.QueueLimit = 0;
    });
    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
});
```
Call `app.UseRateLimiter();` after `app.UseAuthorization();` and before endpoint mapping. In `api/Endpoints/AuthEndpoints.cs`, apply `.RequireRateLimiting("AuthPolicy")` to the `signup` and `login` route registrations specifically (not the whole `/api/auth` group — `/me` and `/logout` don't need it). Once Part B is implemented, apply the same policy to `totp/enroll/confirm` and `totp/verify` too — code-guessing against an MFA challenge is exactly the brute-force case this limiter exists for. The limiter keys by the default partition (client IP via `HttpContext.Connection.RemoteIpAddress`) — note in a one-line comment that if this is ever deployed behind a proxy that doesn't forward the real client IP correctly, this limiter degrades to a single shared bucket for all traffic; confirm `X-Forwarded-For` is honored (it already is, per `app/default.conf.template`'s `proxy_set_header X-Forwarded-For`) and that ASP.NET Core's `ForwardedHeaders` middleware is configured if not already present.

## Minor
- Add `--seed-admin` to the Docker CLI verification command sequence, after `--migrate` and before `up -d`.
- In the new auth-page CSS, reference `var(--accent-sage)`, `var(--accent-terracotta)`, `var(--bg-parchment)` etc. (already defined in `app/src/index.css`) rather than re-typing the hex values.

## Output format
Restate the affected sections of the Part A plan with these corrections folded in, then proceed to implementation in the same file-by-file format as that plan.
```

---

## Part B — Mandatory TOTP second login factor (Google Authenticator-compatible, free)

```
This extends the auth plan already agreed (signup → PendingApproval → admin approve/reject on the dashboard with an automated email → login) with a mandatory TOTP second factor for every user, admin included, using Google Authenticator/Authy-compatible time-based codes (RFC 6238), entirely free — no third-party service, no per-verification cost. Read `api/Models/AppUser.cs`, `api/Endpoints/AuthEndpoints.cs`, `api/Services/JwtTokenService.cs`, and `app/src/pages/Login.jsx` (as they exist after Part A + its corrections) before editing anything.

## Why login changes shape
Login can no longer hand out the real session cookie on a correct password alone. It becomes two calls: password verification returns a short-lived, single-purpose challenge id (not a usable session); a second call exchanges that challenge id plus a 6-digit code for the real httpOnly JWT cookie.

## 1. `api/Models/AppUser.cs` — edit
Add three columns:
- `TotpSecretEncrypted` (string?, column `totp_secret_encrypted`) — the TOTP shared secret, AES-GCM encrypted, never stored or logged in plaintext.
- `TotpEnabled` (bool, default `false`, column `totp_enabled`)
- `LastAcceptedTotpCounter` (long?, column `last_accepted_totp_counter`) — the RFC 6238 time-step counter of the last successfully verified code, so a captured code cannot be replayed a second time within its ~90-second validity window.

## 2. `api/Models/MfaChallenge.cs` (new)
Table `mfa_challenges`, same attribute style as `LessonNote.cs`:
- `Id` (Guid, PK, default `Guid.NewGuid()`, column `id`)
- `UserId` (int, column `user_id`) + `[JsonIgnore] [ForeignKey(nameof(UserId))] public AppUser? User { get; set; }`
- `Purpose` (string, MaxLength 20, column `purpose`) — `"Enrollment"` | `"Login"`
- `CreatedAt` (DateTime, UTC now default, column `created_at`)
- `ExpiresAt` (DateTime, column `expires_at`) — `CreatedAt + 5 minutes`
- `ConsumedAt` (DateTime?, column `consumed_at`)
- `FailedAttempts` (int, default `0`, column `failed_attempts`) — increment on each wrong code; if it reaches 5, treat the challenge as consumed/dead (forces the user to log in again from scratch) rather than allowing indefinite guessing against one challenge.

This is an app table, not a JWT — deliberately never issued through the JwtBearer pipeline, so a partially-authenticated challenge id can never be mistaken for (or misused as) a real session token by any other endpoint.

## 3. `api/Options/AuthOptions.cs` — edit
Add: `string TotpEncryptionKey { get; set; } = string.Empty;` — a 32-byte (Base64-encoded) AES-256 key, env-only secret, required in Production (extend the same startup check added for `JwtSigningKey` in Part A Correction 2 to cover this too — both must be present and correctly sized before the app will start in Production).

## 4. `api/Services/TotpSecretProtector.cs` (new)
Namespace `StudyTracker.Api.Services`. Wraps `System.Security.Cryptography.AesGcm` (built into .NET, no package) using the key from `AuthOptions.TotpEncryptionKey`.
- `string Encrypt(byte[] rawSecret)` — generates a random 12-byte nonce, encrypts with AES-GCM, returns `Base64(nonce || ciphertext || tag)` as one string.
- `byte[] Decrypt(string encrypted)` — reverses it.

## 5. `api/Services/TotpService.cs` (new)
Namespace `StudyTracker.Api.Services`. Implement RFC 6238 exactly as specified — this is easy to get subtly wrong, so follow this precisely rather than approximating:
- `byte[] GenerateSecret()` — 20 random bytes (`RandomNumberGenerator.GetBytes(20)`), i.e. 160 bits, the standard size for Google Authenticator compatibility.
- `string ToBase32(byte[] secret)` — RFC 4648 Base32, no padding (`=` stripped) — needed for the `otpauth://` URI and for displaying a manual-entry code as a fallback to scanning.
- `string BuildOtpAuthUri(string base32Secret, string email)` — `otpauth://totp/Neuralascent:{Uri.EscapeDataString(email)}?secret={base32Secret}&issuer=Neuralascent&algorithm=SHA1&digits=6&period=30`. Must use SHA1 — Google Authenticator does not support SHA256/512 despite RFC 6238 allowing them.
- `long CurrentCounter()` — `DateTimeOffset.UtcNow.ToUnixTimeSeconds() / 30`.
- `string ComputeCode(byte[] secret, long counter)` — 8-byte big-endian counter, `HMACSHA1(secret, counterBytes)`, dynamic truncation per RFC 4226 §5.3 (`offset = hmac[19] & 0x0F`; 4-byte window at `offset` with the top bit masked off; `% 1_000_000`; zero-padded to 6 digits).
- `bool TryVerify(byte[] secret, string code, long? lastAcceptedCounter, out long acceptedCounter)` — checks `CurrentCounter() - 1`, `CurrentCounter()`, `CurrentCounter() + 1` (±30s clock-drift tolerance) against `ComputeCode`, in that order. Reject immediately (return `false` without checking further) if any matching counter is `<= lastAcceptedCounter` — this is the replay guard. On a match, set `acceptedCounter` to the matched counter.

## 6. `api/Endpoints/AuthEndpoints.cs` — edit (replaces the Part A login handler body)
- `POST /api/auth/login` (unchanged request shape) — after verifying the password and confirming `Status == "Approved"`: create an `MfaChallenge` with `Purpose = user.TotpEnabled ? "Login" : "Enrollment"`, save, and return `Results.Ok(new { challengeId, requiresEnrollment = !user.TotpEnabled })` — **do not set the auth cookie here anymore.**
- `POST /api/auth/totp/enroll/start` (`{ challengeId }`) → load the challenge (`Purpose == "Enrollment"`, not expired, not consumed, `FailedAttempts < 5`); generate a new secret via `TotpService.GenerateSecret()`, encrypt and store it on the user as `TotpSecretEncrypted` (not yet `TotpEnabled = true`), return `{ otpAuthUri, manualEntryCode }` for the frontend to render as a QR code and show as a fallback text.
- `POST /api/auth/totp/enroll/confirm` (`{ challengeId, code }`) → decrypt the user's pending secret, `TotpService.TryVerify`; on success set `TotpEnabled = true`, `LastAcceptedTotpCounter = acceptedCounter`, mark the challenge consumed, issue the real JWT cookie exactly as Part A's single-step login used to, return `UserDto`. On failure, increment `FailedAttempts`, return 401 with attempts-remaining in the message.
- `POST /api/auth/totp/verify` (`{ challengeId, code }`) → same shape as `enroll/confirm` but for `Purpose == "Login"` against the user's already-`TotpEnabled` secret; same success/failure handling.
- Apply `.RequireRateLimiting("AuthPolicy")` (the fixed-window limiter from Part A Correction 6) to `login`, `totp/enroll/confirm`, and `totp/verify` specifically — code-guessing against a challenge is exactly the brute-force case that limiter exists for. Keep it on `signup` too, unchanged from Correction 6.

## 7. `api/Data/StudyTrackerContext.cs` — edit
Add `DbSet<MfaChallenge> MfaChallenges`. In `OnModelCreating`, cascade-delete `MfaChallenge` when its `AppUser` is deleted.

## 8. `docker-compose.yml` — edit
Add, next to `Auth__JwtSigningKey`:
```yaml
      Auth__TotpEncryptionKey: ${TOTP_ENCRYPTION_KEY:?TOTP_ENCRYPTION_KEY must be set (32 random bytes, base64: `openssl rand -base64 32`)}
```

## 9. EF Core migration
```
dotnet ef migrations add AddTotpMfa --project api --startup-project api
```

## 10. Frontend — new dependency
Add `qrcode` to `app/package.json` (`npm install qrcode`) — a small, dependency-free, offline QR-rendering library. This is a deliberate, justified new frontend dependency: the TOTP secret must be rendered into a scannable QR code **entirely client-side**, with zero network calls — using any "send us your data, get a QR code back" third-party API would leak the 2FA secret in transit, which defeats the purpose. Do not use such a service.

## 11. `app/src/hooks/useAuth.jsx` — edit
Update `login(email, password)` to call the new two-step flow: `POST /api/auth/login` → returns `{ challengeId, requiresEnrollment }` (not a logged-in user yet) → the hook exposes this pending state rather than resolving `user` immediately. Add `confirmEnrollment(challengeId, code)` and `verifyTotp(challengeId, code)`, both of which, on success, call `refresh()` (re-fetch `/api/auth/me`) to populate `user`.

## 12. `app/src/pages/Login.jsx` — edit
Becomes a two-screen flow:
- Screen 1 (email + password): on submit, call the updated `login`. If `requiresEnrollment`, move to Screen 2a; otherwise Screen 2b.
- Screen 2a (first-time enrollment): call `POST /api/auth/totp/enroll/start`, render the returned `otpAuthUri` as a QR code via the `qrcode` package (canvas or SVG, either is fine), show `manualEntryCode` as selectable text underneath for users who can't scan, prompt for the 6-digit code, submit to `confirmEnrollment`.
- Screen 2b (returning user): prompt for the 6-digit code, submit to `verifyTotp`.
- On success in either 2a or 2b, navigate to `/`.

## Output format
Produce each new file in full. For each edited file, produce only the changed section with 3–5 lines of surrounding context. State both `dotnet ef migrations add` commands (this one and the earlier `AddUserAuth`, if not already run) as instructions, not generated code.
```

---

## Part B — Corrections (apply before implementing Part B's plan)

```
Apply these four corrections to the Part B (TOTP) plan before implementing it.

## 1. Rate limiter window: 15 minutes, not 60 seconds
Program.cs must register `"AuthPolicy"` as a fixed window of `PermitLimit = 10`, `Window = TimeSpan.FromMinutes(15)` — not a 60-second window. A 60-second window is far too permissive for a login/TOTP-code-guessing gate; this is the same policy already defined in the Part A corrections, reused as-is, not redefined with a shorter window.

## 2. Generate the migration with the tool, not by hand
Do not hand-author the migration `.cs` file for `mfa_challenges` and the new `app_users` columns. After `AppUser`, `MfaChallenge`, and `StudyTrackerContext` changes compile, run:
```
dotnet ef migrations add AddTotpMfa --project api --startup-project api
```
and let the tool generate the migration, its `.Designer.cs`, and the updated `StudyTrackerContextModelSnapshot.cs` together — same reasoning as Part A Correction 4: a hand-written migration file without those desyncs the EF model snapshot.

## 3. Add an account-recovery path for a lost authenticator device
As specced, a user who loses their authenticator device (phone lost/reset, app deleted) has no way back into their account — no backup codes, no fallback channel, by design. Add:
- `POST /api/admin/users/{id:int}/reset-totp` (admin-only, same fresh-DB-recheck pattern as other admin endpoints) — sets `TotpEnabled = false`, `TotpSecretEncrypted = null`, `LastAcceptedTotpCounter = null` on the target user, forcing re-enrollment on their next login. This covers every non-admin user.
- For the admin's own lockout (no one above them to reset it), document — in this same file's comments, not as a UI feature — the manual SQL fallback: `UPDATE app_users SET totp_enabled = false, totp_secret_encrypted = NULL, last_accepted_totp_counter = NULL WHERE email = '<admin email>';`, run directly against the database.

## 4. Resolve the `Login.jsx` vs `AuthPage.jsx` split before writing either
Part A already built `AuthPage.jsx` with a sign-in tab that collects email+password. Do not create a separate new `Login.jsx` for the TOTP steps — instead extend `AuthPage.jsx`'s existing sign-in tab with the two-step state machine (password → enrollment-or-verify screen), so one file owns the entire login flow. If `app/src/App.jsx` currently routes `/login` to a standalone `Login.jsx` from an earlier pass, update that route to point at `AuthPage.jsx` instead and remove the now-unused `Login.jsx` rather than leaving both in the tree.

## Output format
Restate the affected sections of the Part B plan with these corrections folded in, then proceed to implementation.
```

---

## Part C — Meta Llama API chat with the $2/day hard budget cap

```
You are extending the Neuralascent repo with the auth system from Parts A and B already in place (`AppUser`, JWT cookie auth via `[Authorize]`/`RequireAuthorization`, `AuthOptions`, TOTP-gated login). This adds a lesson-scoped AI chat feature backed by Meta's Llama API, gated to approved logged-in users, with a hard $2.00/day spend cap enforced before every model call. Read `api/Program.cs`, `api/Data/StudyTrackerContext.cs`, `api/Models/LessonNote.cs`, `api/Models/AppUser.cs`, `api/Endpoints/AuthEndpoints.cs`, `api/Endpoints/ExerciseEndpoints.cs`, `api/Options/ExerciseExecutionOptions.cs`, `app/src/api/client.js`, `app/src/hooks/useAuth.jsx`, `app/src/pages/ChapterReader.jsx` before editing anything.

## Non-goals for this pass
No streaming/SSE (plain JSON response per message). No RAG/pgvector/embeddings. No new NuGet packages — call the Llama API directly with `HttpClient`.

## Important accuracy caveat — verify before wiring real values
Meta's Llama API (`https://llama.developer.meta.com`, API base commonly `https://api.llama.com/v1/`) is relatively new. The request/response field names below are the best-known shape but **must be verified against the current official docs at implementation time** (`https://llama.developer.meta.com/docs/`) — do not assume they're exact. Critically: whatever the real usage/token-count field turns out to be named, the parsing code must be isolated in one method (`TryParseUsage`) so a schema mismatch is a one-method fix, and the budget guard must never silently treat unparseable usage as zero cost (see `LlamaApiClient` below — fallback estimate is mandatory, not optional).

## 1. `api/Options/LlamaApiOptions.cs` (new)
Same pattern as `ExerciseExecutionOptions.cs`. `SectionName = "LlamaApi"`.
- `string ApiKey { get; set; } = string.Empty;` — env-only secret
- `string BaseUrl { get; set; } = "https://api.llama.com/v1/";`
- `string Model { get; set; } = "Llama-4-Maverick-17B-128E-Instruct-FP8";` — placeholder; comment that the exact current model id must be confirmed against the Llama API docs' model list before deploying
- `int TimeoutSeconds { get; set; } = 30;`
- `int MaxHistoryMessages { get; set; } = 10;`
- `int MaxContextCharacters { get; set; } = 6000;`
- `decimal PricePerMillionInputTokensUsd { get; set; } = 0m;` — **default 0, with a comment: "MUST be set from https://llama.developer.meta.com/docs/ pricing page before production use — a 0 here means the cost tracker will under-report spend."**
- `decimal PricePerMillionOutputTokensUsd { get; set; } = 0m;` — same caveat.

## 2. `api/Options/BudgetOptions.cs` (new)
`SectionName = "Budget"`.
- `decimal DailyCapUsd { get; set; } = 2.00m;`
- `int MaxDailyRequests { get; set; } = 500;` — request-count backstop, independent of cost math, so a cost-tracking bug can't silently disable the guard

## 3. `api/Models/ChatConversation.cs`, `api/Models/ChatMessage.cs` (new)
Same style as `api/Models/LessonNote.cs`.

`ChatConversation` → table `chat_conversations`:
- `Id` (Guid, PK, default `Guid.NewGuid()`, column `id`)
- `UserId` (int, column `user_id`) + `[JsonIgnore] [ForeignKey(nameof(UserId))] public AppUser? User { get; set; }` — **required**, every conversation belongs to an authenticated user
- `LessonId` (int?, column `lesson_id`) + `[JsonIgnore] [ForeignKey(nameof(LessonId))] public Lesson? Lesson { get; set; }`
- `Title` (string?, MaxLength 200, column `title`)
- `CreatedAt` / `UpdatedAt` (DateTime, UTC now defaults)
- `Messages` nav: `[JsonIgnore] public List<ChatMessage> Messages { get; set; } = new();`

`ChatMessage` → table `chat_messages`:
- `Id` (Guid, PK, default `Guid.NewGuid()`, column `id`)
- `ConversationId` (Guid, column `conversation_id`) + nav FK
- `Role` (string, MaxLength 20, column `role`) — `"user"` | `"assistant"`
- `Content` (string, column `content`, `text` type, required)
- `ClientRequestId` (string?, MaxLength 100, column `client_request_id`)
- `PromptTokens` (int?, column `prompt_tokens`)
- `CompletionTokens` (int?, column `completion_tokens`)
- `UsageEstimated` (bool, default `false`, column `usage_estimated`) — true when the fallback character-based estimate was used instead of real API-reported usage
- `EstimatedCostUsd` (decimal(10,6), default `0`, column `estimated_cost_usd`)
- `LatencyMs` (int?, column `latency_ms`)
- `ErrorMessage` (string?, column `error_message`)
- `CreatedAt` (DateTime, UTC now default, column `created_at`)

## 4. `api/Models/ChatDtos.cs` (new)
```csharp
public sealed record CreateChatConversationRequest(int? LessonId, string? Title);
public sealed record ChatConversationDto(Guid Id, int? LessonId, string? Title, DateTime CreatedAt);
public sealed record SendChatMessageRequest(string Message, string? ClientRequestId = null);
public sealed record ChatMessageDto(Guid Id, Guid ConversationId, string Role, string Content, DateTime CreatedAt);
public sealed record UsageSummaryDto(decimal SpentTodayUsd, decimal DailyCapUsd, int RequestsToday, int MaxDailyRequests, bool CapReached);
public sealed record UserUsageDto(int UserId, string Email, decimal SpentTodayUsd, int RequestsToday);
```

## 5. `api/Services/LlamaApiClient.cs` (new)
Namespace `StudyTracker.Api.Services`. Constructor: `HttpClient`, `IOptions<LlamaApiOptions>`, `ILogger<LlamaApiClient>`.

`GenerateResult` record (in same file): `(string Text, int? PromptTokens, int? CompletionTokens, bool UsageEstimated, int? LatencyMs)`.

`Task<GenerateResult> GenerateAsync(string systemInstruction, IReadOnlyList<(string Role, string Content)> history, string userMessage, CancellationToken ct)`:
- If `ApiKey` empty, throw `LlamaApiException("Llama API key is not configured.")` (define this exception type in the same file) without making a call.
- `POST {BaseUrl}chat/completions` (adjust path if the verified docs show a different one), `Authorization: Bearer {ApiKey}`, body: `{"model": Model, "messages": [{"role":"system","content":systemInstruction}, ...history mapped to {"role": "user"|"assistant", "content": ...}, {"role":"user","content":userMessage}]}`.
- Measure latency with `Stopwatch`.
- On non-success status, throw `LlamaApiException` with a message that does **not** include the API key or the raw response body verbatim (log the raw body at `LogWarning` for debugging, but keep the thrown message generic).
- Parse the assistant's reply text and, separately, try to parse token usage in `TryParseUsage(JsonElement root, out int? promptTokens, out int? completionTokens)` — isolate this in its own private method exactly so it's a one-method fix if the real field names differ from your best guess. If usage cannot be parsed, do **not** return null/zero — instead compute a fallback estimate: `promptTokens ≈ ceil((systemInstruction + all history content + userMessage).Length / 4.0)`, `completionTokens ≈ ceil(replyText.Length / 4.0)`, and return `UsageEstimated = true` plus a `LogWarning` noting the fallback was used.

## 6. `api/Services/BudgetGuardService.cs` (new)
Namespace `StudyTracker.Api.Services`. Constructor: `StudyTrackerContext`, `IOptions<BudgetOptions>`.

`Task<UsageSummaryDto> GetTodayUsageAsync(CancellationToken ct)` — computes `todayUtcStart = DateTime.UtcNow.Date`, runs one aggregate query: `db.ChatMessages.Where(m => m.Role == "assistant" && m.CreatedAt >= todayUtcStart)` → `SumAsync(m => m.EstimatedCostUsd)` for spend, `CountAsync()` for request count. Returns a `UsageSummaryDto` with `CapReached = spend >= DailyCapUsd || count >= MaxDailyRequests`.

`Task<bool> TryReserveRequestAsync(CancellationToken ct)` — calls `GetTodayUsageAsync`, returns `!summary.CapReached`. Document with a comment that this has a small check-then-act race window under concurrent requests, which is an accepted, explicitly-noted limitation for this traffic scale (not solved with distributed locking here) — but note that even in the race, the loss is bounded to a handful of extra requests, not an unbounded one, since every message's cost is still capped in size by `MaxContextCharacters`/message length.

## 7. `api/Endpoints/ChatEndpoints.cs` (new)
`MapGroup("/api/chat")` with `.RequireAuthorization()` applied to the whole group (any authenticated user — approval is re-checked per-request below, matching the pattern already used in `AuthEndpoints.GetMe`).

Add a `Task<AppUser?> LoadApprovedUserAsync(HttpContext httpContext, StudyTrackerContext db, CancellationToken ct)` local helper: reads the `sub` claim, loads the user fresh from DB, returns `null` if missing or `Status != "Approved"`. Every handler below calls this first and returns 403 via the `Problem` helper if it's `null` — **never trust the JWT's role/status claims alone for this decision**, always re-check current DB state, since approval can be revoked mid-session.

- `POST /api/chat/conversations` → after the approved-user check: validate `LessonId` if provided (`db.Lessons.AnyAsync`), create `ChatConversation` with `UserId` from the loaded user, save, return `Results.Created` with `ChatConversationDto`.
- `POST /api/chat/conversations/{id:guid}/messages` (`SendChatMessageRequest`) →
  1. Approved-user check.
  2. Load conversation `.Include(c => c.Lesson)`; 404 if missing; 403 if `conversation.UserId != currentUser.Id` (users cannot message each other's conversations, including admins — this is a straightforward ownership check, not an admin override).
  3. Reject empty/whitespace message (400).
  4. **Budget check first, before anything else that costs money**: call `budgetGuard.TryReserveRequestAsync(ct)`. If `false`, return `Results.Json(new { message = "The daily AI usage budget has been reached. Please try again after it resets at 00:00 UTC." }, statusCode: 429)` — do not persist a user message, do not call the Llama client, do not deduct anything. This is the hard block.
  5. Idempotency: if `ClientRequestId` supplied and a message with that `ConversationId`+`ClientRequestId` already exists, return the existing assistant reply instead of re-spending budget.
  6. Persist the user's message (`Role = "user"`, `PromptTokens`/`CompletionTokens` null, `EstimatedCostUsd = 0` — user messages don't carry model cost themselves, the assistant reply's usage reflects the whole exchange).
  7. Build `systemInstruction`: a short fixed identity string + lesson title/content truncated to `MaxContextCharacters` if `conversation.Lesson` is not null, clearly labeled as reference material the model should ground its answer in but not treat as instructions.
  8. Load last `MaxHistoryMessages` prior messages for this conversation as history.
  9. Call `llamaClient.GenerateAsync(...)`. On `LlamaApiException`: persist an assistant message with `ErrorMessage` set, `Content` = a short fallback string, `EstimatedCostUsd = 0`, return 502 via `Problem`.
  10. On success: compute `EstimatedCostUsd` from `(PromptTokens/1_000_000m * PricePerMillionInputTokensUsd) + (CompletionTokens/1_000_000m * PricePerMillionOutputTokensUsd)`, persist the assistant message with `PromptTokens`, `CompletionTokens`, `UsageEstimated`, `EstimatedCostUsd`, `LatencyMs`. Update `conversation.UpdatedAt`. Save. Return `Results.Ok(new ChatMessageDto(...))`.
- `GET /api/chat/conversations/{id:guid}/messages` → approved-user + ownership check as above, then return messages ordered by `CreatedAt`, `AsNoTracking()`.

## 8. `api/Endpoints/AdminEndpoints.cs` — edit
Add two more routes to the same `.RequireAuthorization("AdminOnly")` group (with the same fresh-DB-recheck pattern from Part A Correction 5):
- `GET /api/admin/usage/today` → calls `budgetGuard.GetTodayUsageAsync`, returns the `UsageSummaryDto`.
- `GET /api/admin/usage/by-user` → aggregate `ChatMessages` joined to `ChatConversations` for today, grouped by `UserId`, projected to `UserUsageDto` (join `AppUser` for `Email`), ordered by `SpentTodayUsd` descending.

## 9. `api/Data/StudyTrackerContext.cs` — edit
Add `DbSet<ChatConversation> ChatConversations` and `DbSet<ChatMessage> ChatMessages` under a new `// Chat DbSets` comment block. In `OnModelCreating`, configure: `ChatMessage → ChatConversation` cascade delete; `ChatConversation → AppUser` cascade delete (deleting a user removes their chat history); `ChatConversation → Lesson` `DeleteBehavior.SetNull`. Read the existing method body fully first and add after it without reordering anything.

## 10. `api/Program.cs` — edit
- Register options: `builder.Services.AddOptions<LlamaApiOptions>().BindConfiguration(LlamaApiOptions.SectionName);` and `builder.Services.AddOptions<BudgetOptions>().BindConfiguration(BudgetOptions.SectionName);` near the other options registrations.
- `builder.Services.AddHttpClient<LlamaApiClient>((sp, client) => { var o = sp.GetRequiredService<IOptions<LlamaApiOptions>>().Value; client.Timeout = TimeSpan.FromSeconds(o.TimeoutSeconds); });`
- `builder.Services.AddScoped<BudgetGuardService>();`
- Add `app.MapChatEndpoints();` alongside the other `Map*Endpoints()` calls.

## 11. `api/appsettings.json` — edit
Add, alongside the existing `"Auth"`/`"Email"` sections:
```json
"LlamaApi": {
  "BaseUrl": "https://api.llama.com/v1/",
  "Model": "Llama-4-Maverick-17B-128E-Instruct-FP8",
  "TimeoutSeconds": 30,
  "MaxHistoryMessages": 10,
  "MaxContextCharacters": 6000,
  "PricePerMillionInputTokensUsd": 0,
  "PricePerMillionOutputTokensUsd": 0
},
"Budget": {
  "DailyCapUsd": 2.00,
  "MaxDailyRequests": 500
},
```
Leave the two price fields at `0` in the file — they get a real value only from environment/secret configuration once verified, never checked into `appsettings.json`.

## 12. `docker-compose.yml` — edit
In the `api` service `environment:` block, add:
```yaml
      LlamaApi__ApiKey: ${LLAMA_API_KEY:?LLAMA_API_KEY must be set}
      LlamaApi__PricePerMillionInputTokensUsd: ${LLAMA_PRICE_INPUT_PER_M:?LLAMA_PRICE_INPUT_PER_M must be set — verify current pricing at llama.developer.meta.com before deploying}
      LlamaApi__PricePerMillionOutputTokensUsd: ${LLAMA_PRICE_OUTPUT_PER_M:?LLAMA_PRICE_OUTPUT_PER_M must be set — verify current pricing at llama.developer.meta.com before deploying}
```

## 13. EF Core migration
```
dotnet ef migrations add AddChatWithBudgetTracking --project api --startup-project api
```

## 14. `app/src/api/client.js` — edit
Add a `chat` namespace next to `auth`/`admin`:
```javascript
  chat: {
    createConversation: (lessonId, title) => api.post('/api/chat/conversations', { lessonId, title }),
    sendMessage: (conversationId, message, clientRequestId) =>
      api.post(`/api/chat/conversations/${conversationId}/messages`, { message, clientRequestId }),
    getMessages: (conversationId) => apiClient(`/api/chat/conversations/${conversationId}/messages`),
  },
```
And add to `admin`: `usageToday: () => apiClient('/api/admin/usage/today')`, `usageByUser: () => apiClient('/api/admin/usage/by-user')`.

## 15. `app/src/components/common/ChatWidget.jsx` + `.css` (new)
Read `app/src/pages/ChapterReader.jsx`, `app/src/hooks/useAuth.jsx`, and `app/src/components/common/StateViews.jsx` first.

Props: `{ lessonId }`. Uses `useAuth()`. If `!user`, render a small "Sign in to ask the AI assistant" link to `/login` instead of the chat UI. Otherwise: fixed-position floating toggle button (bottom-right) expanding into a slide-up panel — collapsed by default. State: `isOpen`, `conversationId`, `messages`, `draft`, `isSending`, `error`. On send: lazily create a conversation via `api.chat.createConversation(lessonId)` if `conversationId` is null, optimistically append the user message, call `api.chat.sendMessage(conversationId, draft, crypto.randomUUID())`, append the assistant reply on success. On a 429 (`ApiError.status === 429`), show the cap-reached message inline rather than the generic error path. Disable input while `isSending`. Reuse `ChapterReader.css`'s existing color tokens rather than inventing new ones.

## 16. `app/src/pages/ChapterReader.jsx` — edit
Import `ChatWidget` and render `<ChatWidget lessonId={chapter?.id} />` once at the top level of the returned JSX — the fetched-chapter state variable in this file is called `chapter` (`const [chapter, setChapter] = useState(null);`), not `lesson`; use `chapter?.id` to guard against rendering before it loads. One import line, one render line, no other changes.

## Output format
Produce each new file in full. For each edited file, produce only the changed section with 3–5 lines of surrounding context. State both `dotnet ef migrations add` commands as instructions, not generated code. Explicitly call out, in your response after the code, that `LlamaApi:PricePerMillionInputTokensUsd`/`OutputTokensUsd` and the Llama model id must be confirmed against current Meta documentation before this is deployed for real.
```

---

## Final Corrections — apply to the consolidated master plan (Parts A+B+C combined)

```
Apply these two corrections to the consolidated Neuralascent Auth/TOTP/Chat plan (the one that merges Parts A, B, and C into a single implementation pass) before executing it.

## 1. Generate the EF Core migration — this step is missing entirely from the consolidated plan
The consolidated plan correctly stopped hand-authoring migration `.cs` files, but it also dropped the instruction to generate one at all. As written, the manual verification's `docker compose run --rm --no-deps api --migrate` step has no migration to apply — `AppUser`, `MfaChallenge`, `ChatConversation`, and `ChatMessage` are fully wired in code against tables that do not yet exist in Postgres, and every new endpoint will fail at the first query.

Add this as an explicit step, run locally with the .NET SDK (not inside a container — the generated files must exist in `api/Migrations/` *before* `docker compose build`, since the Docker image only bundles what's already on disk):
```bash
dotnet ef migrations add AddAuthTotpAndChat --project api --startup-project api
```
Use one consolidated migration name (`AddAuthTotpAndChat`), not three separate ones — this plan implements `AppUser`, `MfaChallenge`, `ChatConversation`, and `ChatMessage` together in one pass, so one migration matches that. Insert this command immediately before "1. Build & Seed" in the Manual Verification section, and confirm the generated `AddAuthTotpAndChat.cs`, `AddAuthTotpAndChat.Designer.cs`, and the updated `StudyTrackerContextModelSnapshot.cs` are all present before running `docker compose build`.

## 2. Restore the TOTP account-recovery endpoint — dropped during consolidation
Part B's corrections included `POST /api/admin/users/{id:int}/reset-totp`, but it is missing from this consolidated plan's `AdminEndpoints.cs` list (which currently only has approve/reject/usage-today/usage-by-user). Without it, any user who loses their authenticator device — including a regular user the admin should be able to rescue — is permanently locked out with no recovery path.

Add to `api/Endpoints/AdminEndpoints.cs`, in the same `.RequireAuthorization("AdminOnly")` group with the same fresh-DB-recheck pattern (`Role == "Admin"` and `Status == "Approved"` reloaded from the database, not trusted from the JWT claim) already used by the other admin handlers:
- `POST /api/admin/users/{id:int}/reset-totp` → 404 if the target user doesn't exist; otherwise set `TotpEnabled = false`, `TotpSecretEncrypted = null`, `LastAcceptedTotpCounter = null` on that user, save, return the updated `UserDto`. The user must complete TOTP enrollment again on their next login.

This does not cover the admin's own self-lockout (there's no one above them to call this endpoint on their behalf). Add a one-line code comment directly above this endpoint's handler documenting the manual fallback for that specific case, so it isn't lost again:
```
// If the sole admin account itself loses its authenticator device, there is no
// automated recovery path by design (no one above them to call this endpoint).
// Recover manually via:
//   UPDATE app_users SET totp_enabled = false, totp_secret_encrypted = NULL,
//     last_accepted_totp_counter = NULL WHERE email = '<admin email>';
```

## Output format
Restate the affected sections of the consolidated plan with these two corrections folded in — the new migration-generation step in the verification sequence, and the new `reset-totp` endpoint in `AdminEndpoints.cs` — then proceed to implementation.
```

---

## Code Review Findings — implementation review, 2026-09-04

The consolidated plan was implemented. Review verdict: **strong implementation, not ready to push as-is.** Confirmed correct on inspection: `TotpService.cs` is a textbook-correct RFC 6238/4226 implementation (Base32 bit-packing, dynamic truncation, replay guard using `<=` exactly as specified); `Pbkdf2PasswordHasher.cs` is correct at 210k iterations with constant-time comparison; the budget guard in `ChatEndpoints.cs` checks *before* persisting anything or calling the model; `AdminEndpoints.cs`'s `reset-totp` endpoint and its manual-recovery comment are both present verbatim; migrations are genuinely tool-generated (real `// <auto-generated />` header, matching `ProductVersion` annotation); `AuthContext.jsx`/`useAuth.jsx` cleanly avoid duplication (`useAuth.jsx` is a one-line re-export); rate limiting is 15 minutes as corrected; `x-api-key` middleware is untouched; CORS has `AllowCredentials()`; cookies are `HttpOnly`.

Two hardcoded fallback secrets slipped in — the exact anti-pattern this whole package was built to avoid. Both need fixing before this goes anywhere near production.

```
Apply these three fixes to the implemented Neuralascent auth/TOTP/chat code before this is pushed. Read `api/Program.cs`, `api/Services/Auth/TotpSecretProtector.cs`, `api/Services/LlamaApiClient.cs`, and `docker-compose.yml` first.

## 1. Remove the hardcoded JWT signing key fallback — CRITICAL
`api/Program.cs` currently has:
```csharp
var jwtSecret = builder.Configuration["Auth:JwtSigningKey"]
    ?? builder.Configuration["JWT_SIGNING_KEY"]
    ?? builder.Configuration["Jwt:SecretKey"]
    ?? "Neuralascent_Secure_Development_Secret_Key_2026_AtLeast32Bytes!";
```
This is the literal string that signs and validates every JWT if the real key is ever missing, in ANY environment where `builder.Environment.IsProduction()` doesn't match the literal string `"Production"` exactly (a typo'd or non-standard `ASPNETCORE_ENVIRONMENT` value bypasses the separate startup check elsewhere in this file entirely). Anyone who reads this source can forge a valid JWT for any user, including an admin — full authentication bypass, TOTP included, since TOTP only gates issuing a token, not validating a forged one.

Replace with:
```csharp
var jwtSecret = builder.Configuration["Auth:JwtSigningKey"];
if (string.IsNullOrWhiteSpace(jwtSecret))
{
    if (builder.Environment.IsProduction())
    {
        throw new InvalidOperationException("Production configuration error: Auth:JwtSigningKey must be set.");
    }

    // Local-dev-only convenience: a fresh random key each process start — never a fixed string.
    // Sessions will not survive a dev restart; that is intentional and fine.
    jwtSecret = Convert.ToBase64String(System.Security.Cryptography.RandomNumberGenerator.GetBytes(32));
    Console.WriteLine("WARNING: Auth:JwtSigningKey not configured — using an ephemeral random dev-only key. Set Auth__JwtSigningKey for any shared or persistent environment.");
}
```
Drop the `JWT_SIGNING_KEY` and `Jwt:SecretKey` alias lookups entirely — `docker-compose.yml` only ever sets `Auth__JwtSigningKey`, so those aliases are dead paths that add confusion, not resilience. Leave the existing Production startup-validation block elsewhere in `Program.cs` (the one throwing if `authOptions.JwtSigningKey` is empty or under 32 bytes) exactly as it is — it becomes a second, redundant, and now harmless safety net rather than the only thing standing between this bug and a live exploit.

## 2. Remove the hardcoded TOTP encryption key fallback — CRITICAL
`api/Services/Auth/TotpSecretProtector.cs` currently has:
```csharp
rawKeyStr = "Neuralascent_Totp_Key_32_Bytes_Dev_Secret!";
```
Same exposure, different blast radius: a database dump plus this known string decrypts every user's TOTP secret in any environment where `IsProduction()` doesn't match exactly.

Add an `IHostEnvironment` dependency to the constructor (it will resolve automatically from DI — no registration change needed) and replace the fallback:
```csharp
using Microsoft.Extensions.Hosting;
// ...
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
    // ...rest of the existing Base64-decode-or-SHA256-hash logic is unchanged.
}
```

## 3. Restore fail-fast on `LlamaApi__ApiKey` and `Smtp__*` in `docker-compose.yml`, and gate the Llama mock-response fallback behind non-Production
`docker-compose.yml` currently has these as optional (`${VAR:-}`), not required:
```yaml
      Smtp__Host: ${SMTP_HOST:-}
      Smtp__User: ${SMTP_USER:-}
      Smtp__Pass: ${SMTP_PASS:-}
      LlamaApi__ApiKey: ${LLAMA_API_KEY:-}
```
Restore the required, fail-fast form used everywhere else in this file:
```yaml
      Smtp__Host: ${SMTP_HOST:?SMTP_HOST must be set}
      Smtp__User: ${SMTP_USER:?SMTP_USER must be set}
      Smtp__Pass: ${SMTP_PASS:?SMTP_PASS must be set}
      LlamaApi__ApiKey: ${LLAMA_API_KEY:?LLAMA_API_KEY must be set}
```
This alone is not enough for the Llama key, though: `api/Services/LlamaApiClient.cs` currently returns a canned "not configured" chat reply instead of failing when `ApiKey` is empty, with no environment guard — so if this ever runs outside the `docker-compose.yml` path (a directly-run DLL, a different orchestrator, a misconfigured secret), it silently serves fake AI replies to real users forever instead of failing loudly. Not a spend risk (no key means no cost), but a "nobody notices it's broken" risk. Add the same `IHostEnvironment` guard as fix 2:
```csharp
public LlamaApiClient(HttpClient httpClient, IOptions<LlamaApiOptions> options, ILogger<LlamaApiClient> logger, IHostEnvironment env)
{
    // ...existing field assignments, plus: _env = env;
}
```
and in `GenerateCompletionAsync`, where it currently checks `if (string.IsNullOrWhiteSpace(_options.ApiKey))` and returns the mock response unconditionally, change it to:
```csharp
if (string.IsNullOrWhiteSpace(_options.ApiKey))
{
    if (_env.IsProduction())
    {
        throw new InvalidOperationException("LlamaApi:ApiKey is not configured.");
    }
    // existing mock-response block is now dev-only — keep it as-is here.
}
```

## Output format
For each file, produce only the changed section with 3–5 lines of surrounding context — these are small, surgical diffs, not full-file rewrites. Do not touch any other logic in these three files.
```

### Verification, 2026-09-04 (post-fix)

All three fixes above confirmed correctly applied by reading the actual changed files (not just diffing):
- `api/Program.cs` — hardcoded JWT fallback removed, throws in Production, ephemeral random key in dev, written back into `IConfiguration` so `JwtTokenService`'s independent `IOptions<AuthOptions>` read stays consistent with the JwtBearer validation key.
- `api/Services/Auth/TotpSecretProtector.cs` — hardcoded TOTP key fallback removed, same throw/random-dev-key pattern, `IHostEnvironment` correctly added to the constructor.
- `api/Services/LlamaApiClient.cs` — mock-response fallback now gated behind `!env.IsProduction()`, throws otherwise.
- `docker-compose.yml` — `Smtp__Host`/`Smtp__User`/`Smtp__Pass`/`LlamaApi__ApiKey` restored to fail-fast (`:?must be set`).

One new finding from this pass: **`.env.example`** has `ADMIN_PASSWORD=Admin@Neural2026!` — a real-looking, non-obviously-fake value committed to git, unlike the `your_x_here` placeholders around it. Anyone who copies this file to `.env` without noticing and runs `--seed-admin` ends up with an admin account secured by a password sitting in public git history. Also the `SMTP_*` lines are commented out here even though `docker-compose.yml` now requires them. Fix:
```
ADMIN_PASSWORD=change-me-to-a-strong-password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_smtp_user
SMTP_PASS=your_smtp_password
```

**Build verification status:** `npm run build` (frontend) run for real — succeeds cleanly. No .NET SDK or Docker was available in the reviewing environment, so the API side is a careful manual read (every changed line, correct usings, correct signatures across call sites) rather than an actual compiler pass. Run `docker compose -f docker-compose.yml -f docker-compose.dev.yml build api app` as the real final gate before pushing.
