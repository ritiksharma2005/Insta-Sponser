import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def get_config_val(key: str, default: str = "") -> str:
    """Helper to fetch config value from st.session_state, streamlit.secrets, or os.getenv."""
    val = ""
    try:
        import streamlit as st
        if hasattr(st, "session_state") and key in st.session_state and st.session_state[key]:
            val = str(st.session_state[key])
        elif hasattr(st, "secrets") and key in st.secrets:
            val = str(st.secrets[key])
    except Exception:
        pass

    if not val:
        val = os.getenv(key, "")

    return val if val else default

class Settings:
    """Application Settings and Configuration parameters."""
    
    def __init__(self):
        self.LOG_LEVEL: str = get_config_val("LOG_LEVEL", "INFO")
        
        # Execution Limits
        self.DAILY_OUTREACH_LIMIT: int = int(get_config_val("DAILY_OUTREACH_LIMIT", "5"))
        self.MAX_RESEARCH_PER_DAY: int = int(get_config_val("MAX_RESEARCH_PER_DAY", "20"))
        self.MAX_SEARCH_REQUESTS: int = int(get_config_val("MAX_SEARCH_REQUESTS", "10"))
        self.MAX_FOLLOWUPS: int = int(get_config_val("MAX_FOLLOWUPS", "2"))
        
        # API & Keys
        self.LLM_PROVIDER: str = get_config_val("LLM_PROVIDER", "gemini")
        self.OPENAI_API_KEY: str = get_config_val("OPENAI_API_KEY", "")
        self.GEMINI_API_KEY: str = get_config_val("GEMINI_API_KEY", "")
        self.SEARCH_API_KEY: str = get_config_val("SEARCH_API_KEY", "")
        self.SEARCH_ENGINE_ID: str = get_config_val("SEARCH_ENGINE_ID", "")
        
        # Meta / Instagram App Credentials
        self.META_APP_ID: str = get_config_val("META_APP_ID", "")
        self.META_APP_SECRET: str = get_config_val("META_APP_SECRET", "")
        
        # Google Sheets
        self.GOOGLE_SHEETS_CREDENTIALS_JSON: str = get_config_val("GOOGLE_SHEETS_CREDENTIALS_JSON", "")
        self.GOOGLE_SHEET_ID: str = get_config_val("GOOGLE_SHEET_ID", "")
        self.GOOGLE_SHEET_TITLE: str = get_config_val("GOOGLE_SHEET_TITLE", "News NIT IIT Sponsorship Pipeline")
        
        # Storage Paths
        self.BASE_DIR: Path = Path(__file__).resolve().parent.parent
        self.SQLITE_DB_PATH: Path = self.BASE_DIR / get_config_val("SQLITE_DB_PATH", "data/sponsor_engine.db")

    @property
    def DRY_RUN(self) -> bool:
        dry_str = get_config_val("DRY_RUN", "true").lower()
        return dry_str in ("true", "1", "yes")

    @property
    def APPROVAL_REQUIRED(self) -> bool:
        app_str = get_config_val("APPROVAL_REQUIRED", "true").lower()
        return app_str in ("true", "1", "yes")

    @property
    def META_ACCESS_TOKEN(self) -> str:
        return get_config_val("META_ACCESS_TOKEN", "")

    @property
    def INSTAGRAM_BUSINESS_ACCOUNT_ID(self) -> str:
        return get_config_val("INSTAGRAM_BUSINESS_ACCOUNT_ID", "17841467003339347")

def get_settings() -> Settings:
    """Returns fresh application settings, dynamically reading st.secrets and env."""
    return Settings()

def reload_settings() -> Settings:
    """Force reloads settings from environment or secrets."""
    return Settings()
