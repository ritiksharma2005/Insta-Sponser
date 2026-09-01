import logging
from typing import Dict, Any
from sponsor_engine.database.models import Candidate
from sponsor_engine.research.instagram_research import InstagramResearcher
from sponsor_engine.research.website_research import WebsiteResearcher

logger = logging.getLogger(__name__)

class CompanyResearcher:
    """Consolidates public information for candidate organizations."""

    def __init__(self):
        self.ig_researcher = InstagramResearcher()
        self.web_researcher = WebsiteResearcher()

    def research_candidate(self, candidate: Candidate) -> Dict[str, Any]:
        """Conducts thorough public research on a candidate business."""
        logger.info(f"Researching candidate: '{candidate.business_name}' in category '{candidate.category}'")

        ig_data = self.ig_researcher.research_profile(candidate.instagram, candidate.snippet)
        web_data = self.web_researcher.research_website(candidate.website, candidate.snippet)

        # Evaluate target audience relevance
        category_lower = candidate.category.lower()
        if any(w in category_lower for w in ["coaching", "edtech", "housing", "laptop", "college"]):
            student_rel = "High (Direct student relevance)"
            youth_rel = "High"
        elif any(w in category_lower for w in ["sports", "apparel", "cafe", "travel", "gaming"]):
            student_rel = "Medium-High"
            youth_rel = "Very High (Youth & Lifestyle fit)"
        else:
            student_rel = "Medium"
            youth_rel = "Medium"

        # Geographic relevance evaluation
        city_lower = candidate.city.lower()
        if "surat" in city_lower or "gujarat" in city_lower:
            geo_rel = "Very High (Surat/Gujarat regional hub)"
        elif any(c in city_lower for c in ["mumbai", "bengaluru", "delhi", "pune", "ahmedabad", "hyderabad", "jaipur"]):
            geo_rel = "High (Major Indian college hub)"
        else:
            geo_rel = "National (India-wide presence)"

        res = {
            "business_name": candidate.business_name,
            "category": candidate.category,
            "subcategory": candidate.category,
            "city": candidate.city,
            "state": "Gujarat" if "surat" in candidate.city.lower() else "India",
            "country": "India",
            "website": candidate.website,
            "instagram": ig_data["instagram_handle"],
            "followers": ig_data["followers"],
            "social_activity": ig_data["social_activity"],
            "email": web_data["email"],
            "phone": web_data["phone"],
            "description": web_data["description"],
            "target_audience": f"Youth, students & young professionals in {candidate.city}",
            "student_relevance": student_rel,
            "youth_relevance": youth_rel,
            "geographic_relevance": geo_rel,
            "growth_signal": web_data["growth_signal"],
            "discovery_source": candidate.source
        }

        return res
