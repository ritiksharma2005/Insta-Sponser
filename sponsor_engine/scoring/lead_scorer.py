import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)

class LeadScorer:
    """Deterministic 100-Point Lead Scoring Engine for @news.nit_iit."""

    def evaluate_lead(self, research_data: Dict[str, Any]) -> Tuple[int, str, str]:
        """
        Calculates 100-point score, assigns Lead Tier, and generates rationale.
        Returns tuple of (score: int, tier: str, why_suitable: str).
        """
        score = 0
        reasons = []

        # 1. Audience Relevance (Max 30 pts)
        student_rel = str(research_data.get("student_relevance", "")).lower()
        if "direct" in student_rel or "high" in student_rel:
            score += 30
            reasons.append("Direct target audience alignment with Indian college/youth demographic (+30)")
        elif "medium" in student_rel:
            score += 20
            reasons.append("Moderate alignment with college & youth demographic (+20)")
        else:
            score += 10
            reasons.append("Basic youth relevance (+10)")

        # 2. Sponsorship Potential (Max 20 pts)
        category = str(research_data.get("category", "")).lower()
        high_sponsorship_cats = ["coaching", "edtech", "housing", "sports", "apparel", "d2c", "laptop", "events", "ai", "saas"]
        if any(cat in category for cat in high_sponsorship_cats):
            score += 20
            reasons.append("Category shows active commercial marketing & sponsorship potential (+20)")
        else:
            score += 12
            reasons.append("Moderate sponsorship commercial fit (+12)")

        # 3. Audience Overlap (Max 15 pts)
        youth_rel = str(research_data.get("youth_relevance", "")).lower()
        if "very high" in youth_rel or "high" in youth_rel:
            score += 15
            reasons.append("High audience overlap with engineering/medical students and young professionals (+15)")
        else:
            score += 10
            reasons.append("Partial audience overlap (+10)")

        # 4. Business Quality & Legitimacy (Max 10 pts)
        website = research_data.get("website", "")
        email = research_data.get("email", "")
        if website != "Not Available" or email != "Not Available":
            score += 10
            reasons.append("Established public digital presence (+10)")
        else:
            score += 5
            reasons.append("Verified public listing (+5)")

        # 5. Social Activity (Max 10 pts)
        instagram = research_data.get("instagram", "")
        if instagram != "Not Available":
            score += 10
            reasons.append("Active Instagram channel (+10)")
        else:
            score += 5
            reasons.append("Social channel present (+5)")

        # 6. Geographic Relevance (Max 5 pts)
        geo_rel = str(research_data.get("geographic_relevance", "")).lower()
        if "surat" in geo_rel or "gujarat" in geo_rel:
            score += 5
            reasons.append("High local priority: Surat/Gujarat target demographic (+5)")
        else:
            score += 3
            reasons.append("National geographic reach (+3)")

        # 7. Growth / Marketing Signals (Max 5 pts)
        growth_signal = research_data.get("growth_signal", "None detected")
        if growth_signal != "None detected" and growth_signal != "Not Available":
            score += 5
            reasons.append(f"Active growth signal detected ({growth_signal}) (+5)")
        else:
            score += 2
            reasons.append("Baseline marketing activity (+2)")

        # 8. Collaboration Fit (Max 5 pts)
        score += 5
        reasons.append("Clear natural collaboration angles for @news.nit_iit (+5)")

        # Enforce boundary
        score = min(100, max(0, score))

        # Assign Lead Tier
        if score >= 90:
            tier = "HOT"
        elif score >= 75:
            tier = "HIGH"
        elif score >= 60:
            tier = "MEDIUM"
        else:
            tier = "LOW"

        # Construct why_suitable synthesis
        city = research_data.get("city", "India")
        bus_name = research_data.get("business_name", "Business")
        cat_name = research_data.get("category", "General")
        
        why_suitable = (
            f"{bus_name} is a {city}-based {cat_name.lower()} organization with a youth-focused offering. "
            f"News NIT IIT (@news.nit_iit) has a strong student and young audience in India ({research_data.get('geographic_relevance', 'regional focus')}), "
            f"making the page highly relevant for promoting campaigns, product launches, or events. "
            f"Key strengths: {'; '.join(reasons[:3])}."
        )

        logger.info(f"Evaluated lead '{bus_name}': Score={score}/100, Tier={tier}")
        return score, tier, why_suitable
