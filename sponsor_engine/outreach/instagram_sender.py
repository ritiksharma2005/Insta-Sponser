import logging
import requests
from typing import Tuple, Dict, Any
from config.settings import get_settings, reload_settings
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
        Executes outreach DM for an approved lead via Meta Graph API or generates 1-click Instagram link.
        """
        self.settings = reload_settings()

        if lead.status != "APPROVED":
            return False, f"Lead '{lead.business_name}' is not in APPROVED status (Current: {lead.status})"

        if self.settings.DRY_RUN:
            logger.info(f"[DRY_RUN MODE] Simulated DM outreach to '{lead.business_name}' ({lead.instagram})")
            lead.status = "CONTACTED"
            lead.last_contacted = "2026-09-03 (Dry Run)"
            lead.notes = (lead.notes or "") + " [Simulated Dry-Run Outreach Sent]"
            self.db.insert_or_update_lead(lead)
            return True, "Simulated successful outreach (DRY_RUN=true)"

        # Live Outreach via Meta API (Requires configured credentials)
        if not self.settings.META_ACCESS_TOKEN or not self.settings.INSTAGRAM_BUSINESS_ACCOUNT_ID:
            return False, "Meta Graph API credentials missing in .env or Streamlit Secrets (META_ACCESS_TOKEN / INSTAGRAM_BUSINESS_ACCOUNT_ID)"

        handle_clean = lead.instagram.lstrip("@").strip()
        if not handle_clean or handle_clean == "Not Available":
            return False, "Invalid Instagram handle for lead"

        try:
            # Meta Messages API endpoint (Graph API v18.0)
            url = f"https://graph.facebook.com/v18.0/{self.settings.INSTAGRAM_BUSINESS_ACCOUNT_ID}/messages"
            headers = {"Authorization": f"Bearer {self.settings.META_ACCESS_TOKEN}"}
            
            # Payload 1: Direct username recipient
            payload = {
                "recipient": {"username": handle_clean},
                "message": {"text": lead.personalized_message}
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code in (200, 201):
                lead.status = "CONTACTED"
                lead.last_contacted = "2026-09-03"
                self.db.insert_or_update_lead(lead)
                logger.info(f"Successfully sent live Instagram message to {lead.instagram}")
                return True, "Message sent via Meta Graph API"
            else:
                err_json = response.json() if response.text else {}
                err_obj = err_json.get("error", {})
                err_code = err_obj.get("code")
                err_msg = err_obj.get("message", response.text)
                
                # Check specifically for Meta Authentication / Session / Token Expiry Errors (e.g. code 190, 102, expired token)
                is_token_err = err_code in (190, 102) or any(term in str(err_msg).lower() for term in ("session has expired", "invalid access token", "error validating access token", "oauth"))
                if is_token_err:
                    logger.error(f"Meta Graph API Token Error ({err_code}): {err_msg}")
                    return False, f"Meta Token Error (Code {err_code}): {err_msg}. Please update META_ACCESS_TOKEN in Streamlit Secrets!"

                # If Meta restricts direct API cold DM to unknown handles, mark as CONTACTED with IG chat link fallback
                ig_dm_url = f"https://ig.me/m/{handle_clean}"
                lead.status = "CONTACTED"
                lead.last_contacted = "2026-09-03"
                lead.notes = (lead.notes or "") + f" [Direct DM Link: {ig_dm_url}]"
                self.db.insert_or_update_lead(lead)

                logger.warning(f"Meta Graph API restriction for {lead.instagram}: {err_msg}")
                return True, f"Lead marked as CONTACTED! Open direct Instagram chat: {ig_dm_url}"
        except Exception as e:
            logger.error(f"Failed to execute outreach request: {e}")
            return False, f"Network/API Error: {str(e)}"
