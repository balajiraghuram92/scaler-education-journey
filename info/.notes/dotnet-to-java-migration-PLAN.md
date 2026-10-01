# .NET → Java Migration Plan (Neuralascent API)

Decided 2026-10-01. Goal: learn (1) how to migrate a codebase between stacks, (2) how to plan and build a Java backend.

## 1. Decisions (locked)
- Java 21, Spring Boot (latest stable 4.x, else 3.5.x — verify at start), Spring Data JPA, Maven
- Flyway for schema management, **baselined on the existing Postgres schema** (no new schema; shared DB)
- Spring MVC + virtual threads (no WebFlux)
- Module folder: `api-java/`. `ai-agent/` stays Python and is untouched
- Strangler: Java runs beside .NET; proxy (`app/nginx.conf`) routes by path group, one slice at a time
- .NET `api/` is FROZEN: hotfixes only, no new features, no new EF migrations
- **All Java is written by the user.** Claude: concept teaching, hints, review only

## 2. Slice order
| # | Slice | .NET source | Concepts to learn |
|---|-------|-------------|-------------------|
| 0 | Health + config | `/health*`, `appsettings*` | Boot app lifecycle, profiles, `@ConfigurationProperties`, Actuator, Flyway baseline, Docker image |
| 1 | Read-only: reading-map | `/api/reading-map` | JPA entities/mapping to an existing schema, repositories, DTO records, controller layer, `ddl-auto=validate` |
| 2 | Read-only: courses/lessons/atlas | `/api/courses`, `/api/lessons/{id}`, `/api/knowledge-atlas` | Relationships, N+1 and fetch strategy, projections, pagination |
| 3 | Writes | tasks toggle, lessons/problems POST/PUT/PATCH, ingest | Transactions, validation, error handling (`ProblemDetail`), idempotency |
| 4 | Auth + MFA | `AuthEndpoints`, `Services/Auth`, `Email` | Spring Security filter chain, JWT resource server, password hashing, method security, mail |
| 5 | Exercise runner | `ExerciseEndpoints`, `Services/Exercises` | docker-java, process isolation, timeouts, virtual threads in practice |
| 6 | Localization + reconciliation (+ chat/import/admin as needed) | `Services/Localization`, `Services/Reconciliation`, `ChatEndpoints` | Service design, outbound HTTP (`RestClient`), scheduling, testing strategy |

(Localization Lab is ON HOLD as a product; slice 6 is last and may stay in .NET longer.)

## 3. Per-slice checklist
1. Read the .NET endpoint/service; write down its behavior (inputs, outputs, status codes, edge cases) — don't port line by line
2. Design the Java shape yourself (layers, DTOs, errors)
3. Implement
4. Contract-compare: same request to .NET and Java, diff the JSON
5. Tests (unit + integration with Testcontainers Postgres)
6. Route the path in the proxy to Java; watch; keep rollback = revert the proxy rule
7. Log below; mark the .NET endpoint as migrated

## 4. Open items
- Slice-0 detail (Dockerfile, compose service, proxy rule) — decide when we start
- Seed data (`api/Data/*SeedData.cs`) ownership: stays with .NET until a later slice, since the schema is shared

## 5. Status log
- 2026-10-01: stack, schema strategy, folder name, and slice order decided. Nothing built yet.
