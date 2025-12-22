import sys

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database - MUST be set via environment variable in production
    database_url: str = ""

    # Cache settings
    cache_ttl: int = 300
    cache_max_size: int = 10

    # CORS - only used in development when frontend/backend are on different ports
    # In production, frontend and backend are same-origin (no CORS needed)
    cors_origins: str = ""

    # Environment: "development" or "production"
    environment: str = "development"

    class Config:
        env_file = ".env"

    def get_cors_origins(self) -> list[str]:
        """Parse CORS origins for development use."""
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
