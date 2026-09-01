from typing import Optional, Tuple
from sponsor_engine.database.sqlite_db import SQLiteDatabase
from sponsor_engine.database.models import Lead
from sponsor_engine.utils.logging import setup_logger

logger = setup_logger("deduplication")

class DeduplicationEngine:
    """Multi-identifier deduplication checker."""

    def __init__(self, db: Optional[SQLiteDatabase] = None):
        self.db = db or SQLiteDatabase()

    def is_duplicate(
        self,
        instagram: str = "Not Available",
        website: str = "Not Available",
        business_name: str = "",
        email: str = "Not Available",
        phone: str = "Not Available"
    ) -> Tuple[bool, Optional[Lead]]:
        """
        Checks if candidate matches an existing stored lead across multiple identifiers.
        Returns tuple of (is_duplicate: bool, matching_lead: Optional[Lead]).
        """
        existing = self.db.find_duplicate_lead(
            instagram=instagram,
            website=website,
            business_name=business_name,
            email=email,
            phone=phone
        )

        if existing:
            logger.info(f"Duplicate detected for '{business_name}' matching existing lead ID {existing.lead_id} (Status: {existing.status})")
            return True, existing

        return False, None
