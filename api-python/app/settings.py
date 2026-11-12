"""Ported from api/Options/*.cs and the configuration reads in api/Program.cs.

One settings class per file in api/Options/, plus the connection string and
every other configuration key Program.cs reads. Environment variable names
match .NET exactly so both containers can share one .env.
"""

from __future__ import annotations

import os
from decimal import Decimal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    """Ported from api/Options/AuthOptions.cs (section Auth)."""

    model_config = SettingsConfigDict(env_prefix="Auth__", populate_by_name=True, extra="ignore")

    jwt_signing_key: str = Field(default="", alias="Auth__JwtSigningKey")
    jwt_issuer: str = Field(default="neuralascent", alias="Auth__JwtIssuer")
    jwt_audience: str = Field(default="neuralascent-app", alias="Auth__JwtAudience")
    jwt_expiry_minutes: int = Field(default=720, alias="Auth__JwtExpiryMinutes")
    cookie_name: str = Field(default="na_auth", alias="Auth__CookieName")
    access_token_minutes: int = Field(default=30, alias="Auth__AccessTokenMinutes")
    refresh_cookie_name: str = Field(default="na_refresh", alias="Auth__RefreshCookieName")
    remember_me_days: int = Field(default=30, alias="Auth__RememberMeDays")
    session_hours: int = Field(default=24, alias="Auth__SessionHours")
    idle_timeout_days: int = Field(default=14, alias="Auth__IdleTimeoutDays")
    refresh_reuse_grace_seconds: int = Field(default=60, alias="Auth__RefreshReuseGraceSeconds")
    min_password_length: int = Field(default=10, alias="Auth__MinPasswordLength")
    totp_encryption_key: str = Field(default="", alias="Auth__TotpEncryptionKey")


class JwtSettings(BaseSettings):
    """Ported from api/Options/JwtOptions.cs (section Jwt, legacy aliases)."""

    model_config = SettingsConfigDict(env_prefix="Jwt__", populate_by_name=True, extra="ignore")

    secret_key: str = Field(default="", alias="Jwt__SecretKey")
    issuer: str = Field(default="Neuralascent", alias="Jwt__Issuer")
    audience: str = Field(default="NeuralascentLearners", alias="Jwt__Audience")
    expiration_days: int = Field(default=7, alias="Jwt__ExpirationDays")
    cookie_name: str = Field(default="auth_token", alias="Jwt__CookieName")


class EmailSettings(BaseSettings):
    """Ported from api/Options/EmailOptions.cs (section Email)."""

    model_config = SettingsConfigDict(env_prefix="Email__", populate_by_name=True, extra="ignore")

    smtp_host: str = Field(default="", alias="Email__SmtpHost")
    smtp_port: int = Field(default=587, alias="Email__SmtpPort")
    smtp_username: str = Field(default="", alias="Email__SmtpUsername")
    smtp_password: str = Field(default="", alias="Email__SmtpPassword")
    use_ssl: bool = Field(default=True, alias="Email__UseSsl")
    from_address: str = Field(default="noreply@neuralascent.top", alias="Email__FromAddress")
    from_display_name: str = Field(default="Neuralascent", alias="Email__FromDisplayName")


class SmtpSettings(BaseSettings):
    """Ported from api/Options/SmtpOptions.cs (section Smtp)."""

    model_config = SettingsConfigDict(env_prefix="Smtp__", populate_by_name=True, extra="ignore")

    host: str = Field(default="", alias="Smtp__Host")
    port: int = Field(default=587, alias="Smtp__Port")
    username: str = Field(default="", alias="Smtp__Username")
    password: str = Field(default="", alias="Smtp__Password")
    enable_ssl: bool = Field(default=True, alias="Smtp__EnableSsl")
    from_email: str = Field(default="noreply@neuralascent.com", alias="Smtp__FromEmail")
    from_name: str = Field(default="Neuralascent", alias="Smtp__FromName")
    admin_notification_email: str = Field(default="", alias="Smtp__AdminNotificationEmail")
    frontend_url: str = Field(default="http://localhost:5173", alias="Smtp__FrontendUrl")

    @property
    def is_configured(self) -> bool:
        return bool(self.host and self.host.strip())


class ExerciseExecutionSettings(BaseSettings):
    """Ported from api/Options/ExerciseExecutionOptions.cs (section ExerciseExecution)."""

    model_config = SettingsConfigDict(env_prefix="ExerciseExecution__", populate_by_name=True, extra="ignore")

    exercises_root: str = Field(default="", alias="ExerciseExecution__ExercisesRoot")
    workspace_root: str = Field(default="", alias="ExerciseExecution__WorkspaceRoot")
    runner_image: str = Field(
        default="neuralascent-java-runner:dev", alias="ExerciseExecution__RunnerImage"
    )
    runner_images_by_profile: dict[str, str] = Field(
        default_factory=dict, alias="ExerciseExecution__RunnerImagesByProfile"
    )
    python_runner_image: str = Field(
        default="neuralascent-python-runner:dev", alias="ExerciseExecution__PythonRunnerImage"
    )
    docker_endpoint: str = Field(
        default="unix:///var/run/docker.sock", alias="ExerciseExecution__DockerEndpoint"
    )
    maven_cache_volume: str = Field(
        default="neuralascent-maven-cache", alias="ExerciseExecution__MavenCacheVolume"
    )
    max_concurrent_executions: int = Field(default=2, alias="ExerciseExecution__MaxConcurrentExecutions")
    max_file_bytes: int = Field(default=131072, alias="ExerciseExecution__MaxFileBytes")
    max_submission_bytes: int = Field(default=262144, alias="ExerciseExecution__MaxSubmissionBytes")
    max_output_bytes: int = Field(default=65536, alias="ExerciseExecution__MaxOutputBytes")
    max_execution_seconds: int = Field(default=240, alias="ExerciseExecution__MaxExecutionSeconds")
    execution_startup_grace_seconds: int = Field(
        default=15, alias="ExerciseExecution__ExecutionStartupGraceSeconds"
    )
    memory_limit_bytes: int = Field(default=1610612736, alias="ExerciseExecution__MemoryLimitBytes")
    nano_cpus: int = Field(default=1000000000, alias="ExerciseExecution__NanoCpus")
    pids_limit: int = Field(default=128, alias="ExerciseExecution__PidsLimit")
    container_cleanup_grace_seconds: int = Field(
        default=5, alias="ExerciseExecution__ContainerCleanupGraceSeconds"
    )


class LlamaApiSettings(BaseSettings):
    """Ported from api/Options/LlamaApiOptions.cs (section LlamaApi)."""

    model_config = SettingsConfigDict(env_prefix="LlamaApi__", populate_by_name=True, extra="ignore")

    api_key: str = Field(default="", alias="LlamaApi__ApiKey")
    base_url: str = Field(default="https://api.llama.com/v1/", alias="LlamaApi__BaseUrl")
    model: str = Field(
        default="Llama-4-Maverick-17B-128E-Instruct-FP8", alias="LlamaApi__Model"
    )
    timeout_seconds: int = Field(default=30, alias="LlamaApi__TimeoutSeconds")
    max_history_messages: int = Field(default=10, alias="LlamaApi__MaxHistoryMessages")
    max_context_characters: int = Field(default=6000, alias="LlamaApi__MaxContextCharacters")
    price_per_million_input_tokens_usd: Decimal = Field(
        default=Decimal("0"), alias="LlamaApi__PricePerMillionInputTokensUsd"
    )
    price_per_million_output_tokens_usd: Decimal = Field(
        default=Decimal("0"), alias="LlamaApi__PricePerMillionOutputTokensUsd"
    )


class BudgetSettings(BaseSettings):
    """Ported from api/Options/BudgetOptions.cs (section Budget)."""

    model_config = SettingsConfigDict(env_prefix="Budget__", populate_by_name=True, extra="ignore")

    daily_cap_usd: Decimal = Field(default=Decimal("2.00"), alias="Budget__DailyCapUsd")
    max_daily_requests: int = Field(default=500, alias="Budget__MaxDailyRequests")


class AzureTranslatorSettings(BaseSettings):
    """Ported from api/Options/AzureTranslatorOptions.cs (section AzureTranslator)."""

    model_config = SettingsConfigDict(env_prefix="AzureTranslator__", populate_by_name=True, extra="ignore")

    endpoint: str = Field(
        default="https://api.cognitive.microsofttranslator.com",
        alias="AzureTranslator__Endpoint",
    )
    key: str = Field(default="", alias="AzureTranslator__Key")
    region: str = Field(default="", alias="AzureTranslator__Region")


class LocalizationAiSettings(BaseSettings):
    """Ported from api/Options/LocalizationAiOptions.cs (section LocalizationAi)."""

    model_config = SettingsConfigDict(env_prefix="LocalizationAi__", populate_by_name=True, extra="ignore")

    base_url: str = Field(default="", alias="LocalizationAi__BaseUrl")
    shared_secret: str = Field(default="", alias="LocalizationAi__SharedSecret")
    timeout_seconds: int = Field(default=60, alias="LocalizationAi__TimeoutSeconds")
    legacy_mt_price_per_char_usd: Decimal = Field(
        default=Decimal("0"), alias="LocalizationAi__LegacyMtPricePerCharUsd"
    )
    chat_price_per_1k_input_tokens_usd: Decimal = Field(
        default=Decimal("0"), alias="LocalizationAi__ChatPricePer1kInputTokensUsd"
    )
    chat_price_per_1k_output_tokens_usd: Decimal = Field(
        default=Decimal("0"), alias="LocalizationAi__ChatPricePer1kOutputTokensUsd"
    )


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def get_dotnet_connection_string(environment: str = "") -> str:
    """Mirror the connection-string fallback chain in Program.cs lines 25-53."""
    connection_string = _env("ConnectionStrings__DefaultConnection")
    if not connection_string.strip():
        db_host = _env("DATABASE_HOST", "database")
        db_port = _env("DATABASE_PORT", "5432")
        db_name = _env("DATABASE_NAME", "studytracker")
        db_user = _env("DATABASE_USER", "studyuser")
        db_pass = _env("DATABASE_PASSWORD", _env("POSTGRES_PASSWORD"))
        if db_pass.strip():
            connection_string = (
                f"Host={db_host};Port={db_port};Database={db_name};"
                f"Username={db_user};Password={db_pass}"
            )
    if not connection_string.strip():
        if environment.lower() == "production":
            raise RuntimeError("Production database connection configuration is missing.")
        connection_string = "Host=localhost;Database=studytracker;Username=studyuser;Password=studyuserpass"
    return connection_string


def get_environment() -> str:
    return _env("ASPNETCORE_ENVIRONMENT", _env("DOTNET_ENVIRONMENT", "Development"))


def get_frontend_url() -> str:
    return _env("frontend_url", "")


def get_api_key() -> str:
    return _env("api_key", _env("API_KEY", ""))


def get_jwt_config() -> tuple[str, str, str, str]:
    """Return (secret, issuer, audience, cookie_name) using Program.cs fallback order."""
    secret = _env("Auth__JwtSigningKey", _env("Auth:JwtSigningKey", ""))
    issuer = (
        _env("Auth__JwtIssuer")
        or _env("Auth:JwtIssuer")
        or _env("Auth__Issuer")
        or _env("Auth:Issuer")
        or _env("Jwt__Issuer")
        or _env("Jwt:Issuer")
        or "neuralascent"
    )
    audience = (
        _env("Auth__JwtAudience")
        or _env("Auth:JwtAudience")
        or _env("Auth__Audience")
        or _env("Auth:Audience")
        or _env("Jwt__Audience")
        or _env("Jwt:Audience")
        or "neuralascent-app"
    )
    cookie_name = (
        _env("Auth__CookieName") or _env("Auth:CookieName") or _env("Jwt__CookieName") or "na_auth"
    )
    return secret, issuer, audience, cookie_name


class AppSettings(BaseSettings):
    """Aggregate settings; attribute names mirror the C# option class names."""

    model_config = SettingsConfigDict(extra="ignore")

    auth: AuthSettings = Field(default_factory=AuthSettings)
    jwt: JwtSettings = Field(default_factory=JwtSettings)
    email: EmailSettings = Field(default_factory=EmailSettings)
    smtp: SmtpSettings = Field(default_factory=SmtpSettings)
    exercise_execution: ExerciseExecutionSettings = Field(default_factory=ExerciseExecutionSettings)
    llama_api: LlamaApiSettings = Field(default_factory=LlamaApiSettings)
    budget: BudgetSettings = Field(default_factory=BudgetSettings)
    azure_translator: AzureTranslatorSettings = Field(default_factory=AzureTranslatorSettings)
    localization_ai: LocalizationAiSettings = Field(default_factory=LocalizationAiSettings)


_settings: AppSettings | None = None


def get_settings() -> AppSettings:
    global _settings
    if _settings is None:
        _settings = AppSettings()
        # Smtp User/Pass aliases (SmtpOptions.cs exposes User/Pass as aliases).
        user_alias = _env("Smtp__User")
        pass_alias = _env("Smtp__Pass")
        if user_alias:
            _settings.smtp.username = user_alias
        if pass_alias:
            _settings.smtp.password = pass_alias
    return _settings
