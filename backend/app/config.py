import sys

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database - MUST be set via environment variable in production
    database_url: str = ""

    # Cache settings
    cache_ttl: int = 1800
    cache_max_size: int = 10

    # CORS - required in production for S3 frontend, development for separate ports
    # Production: Set to S3 bucket URL(s)
    # Development: Defaults to localhost:5173 if not set
    cors_origins: str = ""

    # Environment: "development" or "production"
    environment: str = "development"

    class Config:
        env_file = (".env", ".env.local")

    def get_cors_origins(self) -> list[str]:
        """Parse CORS origins from environment variable."""
        if self.cors_origins:
            return [
                origin.strip()
                for origin in self.cors_origins.split(",")
                if origin.strip()
            ]

        # Development defaults (Vite dev server)
        if self.environment == "development":
            return [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ]

        return []

    def should_enable_cors(self) -> bool:
        """Determine if CORS middleware should be enabled."""
        # Enable CORS if origins are explicitly configured
        if self.cors_origins:
            return True

        # Enable CORS in development with default origins
        if self.environment == "development":
            return True

        return False

    def validate_production_config(self) -> list[str]:
        """Validate that required settings are configured for production."""
        errors = []

        if self.environment == "production":
            if not self.database_url:
                errors.append("DATABASE_URL is required in production")

            # Validate database URL doesn't contain default/weak credentials
            if self.database_url:
                lower_url = self.database_url.lower()
                if "secret" in lower_url or "password" in lower_url:
                    errors.append("DATABASE_URL appears to contain default credentials")

            # CORS origins required in production for S3 frontend
            if not self.cors_origins:
                errors.append("CORS_ORIGINS is required in production (S3 bucket URL)")

        return errors


settings = Settings()

# Validate configuration on startup
_config_errors = settings.validate_production_config()
if _config_errors:
    print("=" * 50, file=sys.stderr)
    print("CONFIGURATION ERROR", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    for error in _config_errors:
        print(f"  - {error}", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    sys.exit(1)
