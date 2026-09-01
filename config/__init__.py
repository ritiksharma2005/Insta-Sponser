"""Configuration package for News NIT IIT Sponsor Engine."""
from .settings import get_settings, Settings
from .media_profile import get_media_profile, MediaProfile

__all__ = ["get_settings", "Settings", "get_media_profile", "MediaProfile"]
