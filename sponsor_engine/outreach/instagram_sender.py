import logging
import requests
from typing import Tuple, Dict, Any
from config.settings import get_settings
from sponsor_engine.database.models import Lead, OutreachRecord
from sponsor_engine.database.sqlite_db import SQLiteDatabase

logger = logging.getLogger(__name__)

class InstagramSender:
    """Outreach execution module supporting Dry Run simulation and Meta Graph API integration."""

    def __init__(self, db: SQLiteDatabase = None):
        self.settings = get_settings()
        self.db = db or SQLiteDatabase()

    def send_outreach(self, lead: Lead) -> Tuple[bool, str]:
        """
        Executes outreach DM for an approved lead.
        If DRY_RUN=true, simulates outreach safely.
        """
        if lead.status != "APPROVED":
            return False, f"Lead '{lead.business_name}' is not in APPROVED status (Current: {lead.status})"

        if self.settings.DRY_RUN:
            logger.info(f"[DRY_RUN MODE] Simulated DM outreach to '{lead.business_name}' ({lead.instagram})")
            lead.status = "CONTACTED"
            lead.last_contacted = "2026-09-01 (Dry Run)"
            lead.notes = (lead.notes or "") + " [Simulated Dry-Run Outreach Sent]"
            self.db.insert_or_update_lead(lead)
            return True, "Simulated successful outreach (DRY_RUN=true)"

        # Live Outreach via Meta API (Requires configured credentials)
        if not self.settings.META_ACCESS_TOKEN or not self.settings.INSTAGRAM_BUSINESS_ACCOUNT_ID:
            return False, "Meta Graph API credentials missing in .env (META_ACCESS_TOKEN / INSTAGRAM_BUSINESS_ACCOUNT_ID)"

        try:
            # Meta Messages API endpoint (Graph API v18.0)
            url = f"https://graph.facebook.com/v18.0/{self.settings.INSTAGRAM_BUSINESS_ACCOUNT_ID}/messages"
            headers = {"Authorization": f"Bearer {self.settings.META_ACCESS_TOKEN}"}
            payload = {
                "recipient": {"username": lead.instagram.lstrip("@")},
                "message": {"text": lead.personalized_message}
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code in (200, 201):
                lead.status = "CONTACTED"
                lead.last_contacted = "2026-09-01"
                self.db.insert_or_update_lead(lead)
                logger.info(f"Successfully sent live Instagram message to {lead.instagram}")
                return True, "Message sent via Meta Graph API"
            else:
                err_msg = response.text
                logger.error(f"Meta Graph API error for {lead.instagram}: {err_msg}")
                return False, f"Meta API Error: {err_msg}"
        except Exception as e:
            logger.error(f"Failed to execute outreach request: {e}")
            return False, f"Network/API Error: {str(e)}"
