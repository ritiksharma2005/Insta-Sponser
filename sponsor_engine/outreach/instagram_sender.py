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

        # Clean handle
        handle_clean = lead.instagram.lstrip("@").strip()
        if not handle_clean or handle_clean == "Not Available":
            return False, "Invalid Instagram handle for lead"

        ig_dm_url = f"https://ig.me/m/{handle_clean}"

        # If token/credentials are missing, fall back to 1-Click IG Chat
        if not self.settings.META_ACCESS_TOKEN or not self.settings.INSTAGRAM_BUSINESS_ACCOUNT_ID:
            lead.status = "CONTACTED"
            lead.last_contacted = "2026-09-04"
            lead.notes = (lead.notes or "") + f" [Direct DM Link: {ig_dm_url}]"
            self.db.insert_or_update_lead(lead)
            return True, f"1-Click Direct IG Chat ready for @{handle_clean}! Click 'Open IG Chat' below to send message."

        try:
            # Meta Messages API endpoint (Graph API v18.0)
            url = f"https://graph.facebook.com/v18.0/{self.settings.INSTAGRAM_BUSINESS_ACCOUNT_ID}/messages"
            headers = {"Authorization": f"Bearer {self.settings.META_ACCESS_TOKEN}"}
            
            payload = {
                "recipient": {"username": handle_clean},
                "message": {"text": lead.personalized_message}
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            if response.status_code in (200, 201):
                lead.status = "CONTACTED"
                lead.last_contacted = "2026-09-04"
                self.db.insert_or_update_lead(lead)
                logger.info(f"Successfully sent live Instagram message to {lead.instagram}")
                return True, f"Live Instagram Message sent via Meta Graph API to @{handle_clean}!"
            else:
                err_json = response.json() if response.text else {}
                err_obj = err_json.get("error", {})
                err_code = err_obj.get("code")
                err_msg = err_obj.get("message", response.text)
                
                # Check for Meta Token Expiry or API restriction
                is_token_err = err_code in (190, 102) or any(term in str(err_msg).lower() for term in ("session has expired", "invalid access token", "error validating access token", "oauth"))
                
                lead.status = "CONTACTED"
                lead.last_contacted = "2026-09-04"
                lead.notes = (lead.notes or "") + f" [Direct DM Link: {ig_dm_url}]"
                self.db.insert_or_update_lead(lead)

                if is_token_err:
                    logger.warning(f"Meta Token Expired: {err_msg}. Using 1-Click IG Chat fallback.")
                    return True, f"1-Click IG Chat Ready! Click 'Open IG Chat' below to message @{handle_clean} directly."
                else:
                    logger.warning(f"Meta Graph API restriction for {lead.instagram}: {err_msg}")
                    return True, f"Lead marked as CONTACTED! Open direct Instagram chat: {ig_dm_url}"
        except Exception as e:
            lead.status = "CONTACTED"
            lead.last_contacted = "2026-09-04"
            lead.notes = (lead.notes or "") + f" [Direct DM Link: {ig_dm_url}]"
            self.db.insert_or_update_lead(lead)
            logger.error(f"Failed to execute outreach request: {e}")
            return True, f"1-Click Direct Chat ready! Open Instagram DM: {ig_dm_url}"
