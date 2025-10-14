from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ---------------------------
    # Twilio Settings
    # ---------------------------
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str
    TWILIO_CALLBACK_URL: str

    # ---------------------------
    # CallHippo Settings
    # ---------------------------
    CALLHIPPO_API_KEY: str
    CALLHIPPO_USER_ID: str
    CALLHIPPO_AGENT_NUMBER: str

    # ---------------------------
    # AI Services
    # ---------------------------
    OPENAI_API_KEY: str
    ELEVENLABS_API_KEY: str

    # ---------------------------
    # JWT Secret
    # ---------------------------
    SECRET_KEY: str

    # ---------------------------
    # Redis Settings (for Celery)
    # ---------------------------
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"

settings = Settings()
