"""
Application Configuration
Environment variables and settings
"""

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # Application
    APP_NAME: str = "StarCiti Sales Agent API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/starciti_sales")

    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")
    ELEVENLABS_VOICE_ID: str = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")

    # Email Settings
    SENDGRID_FROM_EMAIL: str = os.getenv("SENDGRID_FROM_EMAIL", "noreply@starcitisales.com")
    SENDGRID_FROM_NAME: str = os.getenv("SENDGRID_FROM_NAME", "StarCiti Sales Agent")

    # Frontend
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # CORS
    @property
    def ALLOWED_ORIGINS(self) -> list[str]:
        """Dynamically build CORS origins list"""
        origins = [
            "http://localhost:5173",  # Vite dev server
            "http://localhost:3000",  # Alternative frontend port
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
            "http://localhost:5174",  # Alternative Vite port
        ]

        # Add production frontend URL if set
        if self.FRONTEND_URL and self.FRONTEND_URL not in origins:
            origins.append(self.FRONTEND_URL)

        # Add any additional origins from environment
        extra_origins = os.getenv("EXTRA_CORS_ORIGINS", "")
        if extra_origins:
            origins.extend([o.strip() for o in extra_origins.split(",") if o.strip()])

        return origins

    # AI Models
    CLAUDE_MODEL: str = "claude-3-5-sonnet-20241022"
    WHISPER_MODEL: str = "whisper-1"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # File Storage
    UPLOADS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "../uploads")
    OUTPUTS_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "../outputs")

    class Config:
        env_file = ".env"
        case_sensitive = True


# Create global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Dependency function to get settings"""
    return settings
