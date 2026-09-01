from pydantic import BaseModel, Field
from typing import List, Dict, Any

class MediaProfile(BaseModel):
    """Configurable media profile for @news.nit_iit."""
    instagram_handle: str = Field(default="@news.nit_iit")
    followers: str = Field(default="2,500+")
    monthly_views: str = Field(default="80 lakh+")
    audience_country: str = Field(default="India")
    strong_region: str = Field(default="Surat/Gujarat")
    audience_segments: List[str] = Field(
        default_factory=lambda: [
            "Engineering college students",
            "IIT/NIT students",
            "Medical college students",
            "University & college students",
            "Young people & young professionals"
        ]
    )
    positioning: str = Field(
        default="Indian student and youth-focused media & news platform"
    )
    contact_email: str = Field(default="news.nit.iit@gmail.com")
    collaboration_info: str = Field(
        default="Offers sponsored Instagram posts, reels, stories, campus offer campaigns, and event promotions."
    )

    def get_stats_summary(self) -> str:
        """Returns standard statistics summary for outreach messages."""
        return (
            f"News NIT IIT ({self.instagram_handle}) is a student-focused news and information platform "
            f"with {self.followers} followers and {self.monthly_views} monthly views. "
            f"Our audience is spread across India, with a strong presence among engineering, medical "
            f"and college students and young people (especially in {self.strong_region})."
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for database storage."""
        return self.model_dump()

_media_profile_instance = None

def get_media_profile() -> MediaProfile:
    """Singleton getter for media profile configuration."""
    global _media_profile_instance
    if _media_profile_instance is None:
        _media_profile_instance = MediaProfile()
    return _media_profile_instance

def update_media_profile(profile_data: Dict[str, Any]) -> MediaProfile:
    """Update active media profile configuration."""
    global _media_profile_instance
    _media_profile_instance = MediaProfile(**profile_data)
    return _media_profile_instance
