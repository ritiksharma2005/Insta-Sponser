from typing import Dict, Any, List
from sponsor_engine.database.sqlite_db import SQLiteDatabase
from sponsor_engine.database.models import Lead

class AnalyticsEngine:
    """Calculates lead pipeline performance and conversion statistics."""

    def __init__(self, db: SQLiteDatabase = None):
        self.db = db or SQLiteDatabase()

    def get_summary_metrics(self) -> Dict[str, Any]:
        """Calculates current pipeline summary metrics."""
        leads: List[Lead] = self.db.get_all_leads()
        
        total_leads = len(leads)
        hot_leads = sum(1 for l in leads if l.lead_tier == "HOT")
        high_leads = sum(1 for l in leads if l.lead_tier == "HIGH")
        medium_leads = sum(1 for l in leads if l.lead_tier == "MEDIUM")
        low_leads = sum(1 for l in leads if l.lead_tier == "LOW")

        pending_approval = sum(1 for l in leads if l.status == "APPROVAL_PENDING")
        approved_leads = sum(1 for l in leads if l.status == "APPROVED")
        contacted_leads = sum(1 for l in leads if l.status in ("CONTACTED", "FOLLOW_UP"))
        replied_leads = sum(1 for l in leads if l.status in ("REPLIED", "INTERESTED", "NEGOTIATING", "CONVERTED"))
        interested_leads = sum(1 for l in leads if l.status in ("INTERESTED", "NEGOTIATING", "CONVERTED"))
        converted_leads = sum(1 for l in leads if l.status == "CONVERTED")

        reply_rate = (replied_leads / contacted_leads * 100) if contacted_leads > 0 else 0.0
        conversion_rate = (converted_leads / contacted_leads * 100) if contacted_leads > 0 else 0.0

        # Category Breakdown
        categories: Dict[str, int] = {}
        cities: Dict[str, int] = {}

        for l in leads:
            categories[l.category] = categories.get(l.category, 0) + 1
            cities[l.city] = cities.get(l.city, 0) + 1

        best_category = max(categories, key=categories.get) if categories else "None"
        best_city = max(cities, key=cities.get) if cities else "None"

        return {
            "total_leads": total_leads,
            "hot_leads": hot_leads,
            "high_leads": high_leads,
            "medium_leads": medium_leads,
            "low_leads": low_leads,
            "pending_approval": pending_approval,
            "approved_leads": approved_leads,
            "contacted_leads": contacted_leads,
            "replied_leads": replied_leads,
            "interested_leads": interested_leads,
            "converted_leads": converted_leads,
            "reply_rate": round(reply_rate, 1),
            "conversion_rate": round(conversion_rate, 1),
            "best_category": best_category,
            "best_city": best_city,
            "category_breakdown": categories,
            "city_breakdown": cities
        }
