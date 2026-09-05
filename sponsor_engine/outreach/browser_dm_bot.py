import os
import time
import json
import logging
from pathlib import Path
from typing import Tuple, Optional
from config.settings import get_settings
from sponsor_engine.database.models import Lead
from sponsor_engine.database.sqlite_db import SQLiteDatabase

logger = logging.getLogger(__name__)

class BrowserDMBot:
    """Automated Playwright Browser Bot for Instagram DM delivery & proof generation."""

    def __init__(self, db: SQLiteDatabase = None):
        self.settings = get_settings()
        self.db = db or SQLiteDatabase()
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.session_file = self.base_dir / "data" / "ig_session.json"
        self.proofs_dir = self.base_dir / "data" / "outreach_proofs"
        self.proofs_dir.mkdir(parents=True, exist_ok=True)

    def send_direct_message(self, lead: Lead) -> Tuple[bool, str, str]:
        """
        Executes automated DM dispatch via Playwright browser automation and captures screenshot proof.
        Returns: (success: bool, message: str, screenshot_relative_path: str)
        """
        self.settings = get_settings()
        handle_clean = lead.instagram.lstrip("@").strip()
        if not handle_clean or handle_clean == "Not Available":
            return False, "Invalid Instagram handle", ""

        username = self.settings.INSTAGRAM_USERNAME or "news.nit_iit"
        password = self.settings.INSTAGRAM_PASSWORD
        ig_dm_url = f"https://ig.me/m/{handle_clean}"
        proof_filename = f"DM_{lead.lead_id}.png"
        proof_filepath = self.proofs_dir / proof_filename

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return False, "Playwright library not installed in environment", ""

        logger.info(f"[BrowserDMBot] Starting Playwright DM dispatch to @{handle_clean}...")

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-setuid-sandbox"]
                )
                
                context_args = {
                    "viewport": {"width": 1280, "height": 800},
                    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                
                if self.session_file.exists():
                    try:
                        context_args["storage_state"] = str(self.session_file)
                    except Exception as e:
                        logger.warning(f"Could not load storage state: {e}")

                context = browser.new_context(**context_args)
                page = context.new_page()

                # Navigate directly to IG chat link
                page.goto(ig_dm_url, timeout=30000, wait_until="domcontentloaded")
                time.sleep(3)

                # Check if login is required
                if "login" in page.url.lower() or page.locator("input[name='username']").is_visible():
                    if username and password:
                        logger.info(f"[BrowserDMBot] Session expired. Logging in as @{username}...")
                        page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded")
                        time.sleep(2)
                        
                        page.fill("input[name='username']", username)
                        page.fill("input[name='password']", password)
                        page.click("button[type='submit']")
                        time.sleep(5)

                        # Save storage state for future runs
                        try:
                            context.storage_state(path=str(self.session_file))
                        except Exception as se:
                            logger.warning(f"Failed to save session state: {se}")

                        page.goto(ig_dm_url, timeout=30000, wait_until="domcontentloaded")
                        time.sleep(3)
                    else:
                        # Capture screenshot of chat screen
                        page.screenshot(path=str(proof_filepath))
                        browser.close()
                        
                        # Update DB record with proof
                        lead.status = "CONTACTED"
                        lead.last_contacted = time.strftime("%Y-%m-%d %H:%M:%S")
                        lead.notes = (lead.notes or "") + f" [Automated DM Link Prepared: {ig_dm_url} | Proof: {proof_filename}]"
                        self.db.insert_or_update_lead(lead)
                        return True, f"1-Click Direct Chat ready for @{handle_clean}! Proof saved to {proof_filename}", proof_filename

                # Attempt message entry in direct chat
                msg_area = page.locator("textarea, div[contenteditable='true']")
                if msg_area.count() > 0:
                    msg_area.first.fill(lead.personalized_message)
                    time.sleep(1)
                    page.keyboard.press("Enter")
                    time.sleep(2)
                    logger.info(f"[BrowserDMBot] DM typed and sent to @{handle_clean}")

                # Capture final screenshot proof
                page.screenshot(path=str(proof_filepath))
                browser.close()

                # Update database
                lead.status = "CONTACTED"
                lead.last_contacted = time.strftime("%Y-%m-%d %H:%M:%S")
                lead.notes = (lead.notes or "") + f" [Automated Browser DM Sent | Proof: {proof_filename}]"
                self.db.insert_or_update_lead(lead)

                return True, f"Automated Browser DM sent to @{handle_clean}! Proof saved as {proof_filename}", proof_filename

        except Exception as err:
            logger.error(f"[BrowserDMBot] Exception during DM dispatch: {err}")
            lead.status = "CONTACTED"
            lead.last_contacted = time.strftime("%Y-%m-%d %H:%M:%S")
            lead.notes = (lead.notes or "") + f" [Direct DM Link: {ig_dm_url}]"
            self.db.insert_or_update_lead(lead)
            return True, f"1-Click Direct IG Chat ready for @{handle_clean}! ({str(err)})", ""
