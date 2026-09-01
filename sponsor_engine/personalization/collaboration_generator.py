import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class CollaborationGenerator:
    """Generates tailored collaboration proposals based on category and business signals."""

    def suggest_collaboration(self, research_data: Dict[str, Any]) -> str:
        """Selects natural collaboration model for the target organization."""
        category = str(research_data.get("category", "")).lower()
        city = research_data.get("city", "Surat")
        growth_signal = research_data.get("growth_signal", "")

        if "coaching" in category or "education" in category:
            return "Promote upcoming admission batches, exam prep courses, or scholarship trials via dedicated Instagram Reels & Story links."
        elif "edtech" in category or "skill" in category or "career" in category:
            return "Highlight certification courses, internship opportunities, or career prep tools through dedicated Reel features & link-in-bio highlights."
        elif "sports" in category or "gym" in category:
            return f"Promote upcoming trials, coaching programs, or sports events to active youth in {city} via Instagram Reel showcase & Story updates."
        elif "housing" in category or "pg" in category:
            return f"Feature student PG/accommodation listings, campus proximity details, and student discount codes for college youth in {city}."
        elif "laptop" in category or "mobile" in category or "electronics" in category:
            return f"Run student gadget offer campaigns, laptop rental highlights, or store launch announcements targeting Surat college students."
        elif "ai" in category or "saas" in category or "startup" in category:
            return "Introduce AI tools and tech platforms to engineering & university students through a product showcase Reel and early-adopter access campaign."
        elif "fashion" in category or "d2c" in category or "apparel" in category:
            return "Host a student giveaway or exclusive student promo code showcase with custom Instagram Reel aesthetic featuring the brand."
        elif "food" in category or "cafe" in category or "restaurant" in category:
            return f"Promote local cafe offers, student hangouts, and menu specials to college students in {city} through Reel recommendations."
        else:
            return f"Featured Instagram Reel & Story campaign targeting Indian college students and young people, highlighting {research_data.get('business_name')}."
