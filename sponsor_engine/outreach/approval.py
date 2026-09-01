import logging
from typing import List, Optional
from sponsor_engine.database.sqlite_db import SQLiteDatabase
from sponsor_engine.database.models import Lead

logger = logging.getLogger(__name__)

class ApprovalManager:
    """Manages human approval lifecycle for sponsor leads."""

    def __init__(self, db: SQLiteDatabase = None):
        self.db = db or SQLiteDatabase()

    def get_pending_leads(self) -> List[Lead]:
        """Returns leads awaiting human review (APPROVAL_PENDING)."""
        all_leads = self.db.get_all_leads()
        return [l for l in all_leads if l.status == "APPROVAL_PENDING"]

    def approve_lead(self, lead_id: str, custom_message: Optional[str] = None) -> bool:
        """Approves a lead for outreach execution."""
        lead = self.db.get_lead_by_id(lead_id)
        if not lead:
            return False

        new_msg = custom_message if custom_message else lead.personalized_message
        lead.personalized_message = new_msg
        lead.status = "APPROVED"
        self.db.insert_or_update_lead(lead)
        logger.info(f"Lead ID {lead_id} ('{lead.business_name}') APPROVED by user.")
        return True

    def reject_lead(self, lead_id: str, reason: str = "") -> bool:
        """Rejects a lead."""
        self.db.update_lead_status(lead_id, "REJECTED", notes=f"Rejected by human review: {reason}")
        logger.info(f"Lead ID {lead_id} REJECTED.")
        return True

    def edit_lead_message(self, lead_id: str, new_message: str) -> bool:
        """Edits the personalized message for a lead."""
        lead = self.db.get_lead_by_id(lead_id)
        if not lead:
            return False

        lead.personalized_message = new_message
        self.db.insert_or_update_lead(lead)
        logger.info(f"Updated outreach message for Lead ID {lead_id}.")
        return True
