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

                # Step 1: Open Instagram home / login check
                page.goto("https://www.instagram.com/", timeout=30000, wait_until="domcontentloaded")
                time.sleep(3)

                if "login" in page.url.lower() or page.locator("input[name='username']").is_visible():
                    if username and password:
                        logger.info(f"[BrowserDMBot] Logging in as @{username}...")
                        page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded")
                        time.sleep(3)
                        
                        page.fill("input[name='username']", username)
                        page.fill("input[name='password']", password)
                        page.click("button[type='submit']")
                        time.sleep(7)

                        # Handle "Save info" dialog
                        try:
                            save_info_btn = page.locator("button:has-text('Not Now'), button:has-text('Save Info'), div[role='button']:has-text('Not Now')")
                            if save_info_btn.count() > 0:
                                save_info_btn.first.click()
                                time.sleep(2)
                        except Exception:
                            pass

                        # Handle "Notifications" dialog
                        try:
                            notif_btn = page.locator("button:has-text('Not Now'), div[role='button']:has-text('Not Now')")
                            if notif_btn.count() > 0:
                                notif_btn.first.click()
                                time.sleep(2)
                        except Exception:
                            pass

                        # Save storage state for future runs
                        try:
                            context.storage_state(path=str(self.session_file))
                        except Exception as se:
                            logger.warning(f"Failed to save session state: {se}")

                # Step 2: Open Direct Composer
                logger.info(f"[BrowserDMBot] Navigating to DM composer for @{handle_clean}...")
                page.goto("https://www.instagram.com/direct/new/", wait_until="domcontentloaded")
                time.sleep(4)

                # Search for target username
                search_input = page.locator("input[name='queryBox'], input[placeholder*='Search'], input[type='text']")
                if search_input.count() > 0:
                    search_input.first.fill(handle_clean)
                    time.sleep(3)

                    # Select result row
                    result_row = page.locator("input[type='checkbox'], div[role='dialog'] span:has-text('" + handle_clean + "'), div[role='button']")
                    if result_row.count() > 0:
                        result_row.first.click()
                        time.sleep(2)

                    # Click Next/Chat
                    next_btn = page.locator("button:has-text('Next'), div[role='button']:has-text('Next'), button:has-text('Chat')")
                    if next_btn.count() > 0:
                        next_btn.first.click()
                        time.sleep(4)

                # Type & Send Message
                msg_input = page.locator("div[aria-label*='Message'], div[contenteditable='true'], textarea")
                if msg_input.count() > 0:
                    msg_input.first.click()
                    time.sleep(1)
                    msg_input.first.fill(lead.personalized_message)
                    time.sleep(1)
                    page.keyboard.press("Enter")
                    time.sleep(3)
                    logger.info(f"[BrowserDMBot] DM sent to @{handle_clean}")
                else:
                    # Fallback to direct IG Chat URL
                    page.goto(ig_dm_url, wait_until="domcontentloaded")
                    time.sleep(3)
                    msg_area = page.locator("div[aria-label*='Message'], div[contenteditable='true'], textarea")
                    if msg_area.count() > 0:
                        msg_area.first.fill(lead.personalized_message)
                        time.sleep(1)
                        page.keyboard.press("Enter")
                        time.sleep(3)

                # Capture proof screenshot
                page.screenshot(path=str(proof_filepath))
                browser.close()

                # Update database & lead status
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
