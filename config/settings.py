import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    """Application Settings and Configuration parameters."""
    
    # System Flags
    DRY_RUN: bool = os.getenv("DRY_RUN", "true").lower() in ("true", "1", "yes")
    APPROVAL_REQUIRED: bool = os.getenv("APPROVAL_REQUIRED", "true").lower() in ("true", "1", "yes")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Execution Limits
    DAILY_OUTREACH_LIMIT: int = int(os.getenv("DAILY_OUTREACH_LIMIT", "5"))
    MAX_RESEARCH_PER_DAY: int = int(os.getenv("MAX_RESEARCH_PER_DAY", "20"))
    MAX_SEARCH_REQUESTS: int = int(os.getenv("MAX_SEARCH_REQUESTS", "10"))
    MAX_FOLLOWUPS: int = int(os.getenv("MAX_FOLLOWUPS", "2"))
    
    # API & Keys
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    SEARCH_API_KEY: str = os.getenv("SEARCH_API_KEY", "")
    SEARCH_ENGINE_ID: str = os.getenv("SEARCH_ENGINE_ID", "")
    
    # Meta / Instagram
    META_ACCESS_TOKEN: str = os.getenv("META_ACCESS_TOKEN", "")
    INSTAGRAM_BUSINESS_ACCOUNT_ID: str = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")
    META_APP_ID: str = os.getenv("META_APP_ID", "")
    META_APP_SECRET: str = os.getenv("META_APP_SECRET", "")
    
    # Google Sheets
    GOOGLE_SHEETS_CREDENTIALS_JSON: str = os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON", "")
    GOOGLE_SHEET_ID: str = os.getenv("GOOGLE_SHEET_ID", "")
    GOOGLE_SHEET_TITLE: str = os.getenv("GOOGLE_SHEET_TITLE", "News NIT IIT Sponsorship Pipeline")
    
    # Storage Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    SQLITE_DB_PATH: Path = BASE_DIR / os.getenv("SQLITE_DB_PATH", "data/sponsor_engine.db")

_settings_instance = None

def get_settings() -> Settings:
    """Singleton getter for application settings."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
    return _settings_instance
