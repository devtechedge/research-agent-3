from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    environment: str = os.getenv("ENVIRONMENT", "dev")
    recipient_email: str = os.getenv("RECIPIENT_EMAIL", "devayanmandal@gmail.com")
    simulation_mode: bool = os.getenv("SIMULATION_MODE", "true").lower() == "true"
    email_user: str = os.getenv("EMAIL_USER", "")
    email_app_password: str = os.getenv("EMAIL_APP_PASSWORD", "")
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "postgresql://localhost:5432/lyme_agent")
    use_database: bool = os.getenv("USE_DATABASE", "false").lower() == "true"


settings = Settings()
