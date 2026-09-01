import json
import logging
from typing import List, Optional
from config.settings import get_settings
from config.media_profile import get_media_profile, MediaProfile
from sponsor_engine.database.models import Lead, SearchHistoryRecord, OutreachRecord
from sponsor_engine.database.sqlite_db import SQLiteDatabase

logger = logging.getLogger(__name__)

# Required Google Sheet Headers
LEADS_HEADER = [
    "Lead ID", "Date Found", "Business Name", "Category", "Subcategory", "City", "State", "Country",
    "Website", "Instagram", "Followers", "LinkedIn", "Email", "Phone", "Description", "Target Audience",
    "Student Relevance", "Youth Relevance", "Geographic Relevance", "Social Activity", "Growth Signal",
    "Discovery Source", "Research Date", "Lead Score", "Lead Tier", "Why Suitable", "Suggested Collaboration",
    "Personalized Message", "Status", "Last Contacted", "Next Follow-up", "Response", "Notes"
]

MEDIA_PROFILE_HEADER = [
    "Instagram Handle", "Followers", "Monthly Views", "Audience Country", "Strong Location",
    "Audience Type", "Page Description", "Positioning", "Contact Email", "Collaboration Information"
]

OUTREACH_HEADER = [
    "Lead ID", "Business", "Message", "Generated Date", "Approved", "Sent Date", "Response", "Follow-up Date", "Status"
]

SEARCH_HISTORY_HEADER = [
    "Date", "Category", "Keyword", "Location", "Source", "Candidates Found", "Qualified Leads", "Rejected Leads"
]

ANALYTICS_HEADER = [
    "Metric", "Value", "Notes"
]

class GoogleSheetsManager:
    """Manages reading and writing data to Google Sheets with automatic SQLite sync."""

    def __init__(self):
        self.settings = get_settings()
        self.sqlite_db = SQLiteDatabase()
        self.client = None
        self.spreadsheet = None
        self.is_connected = False

        self._connect()

    def _connect(self):
        """Attempts connection to Google Sheets API."""
        if not self.settings.GOOGLE_SHEETS_CREDENTIALS_JSON or not self.settings.GOOGLE_SHEET_ID:
            logger.info("Google Sheets credentials or Sheet ID not provided. Running in SQLite-only mode.")
            return

        try:
            import gspread
            from google.oauth2.service_account import Credentials

            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]

            creds_dict = json.loads(self.settings.GOOGLE_SHEETS_CREDENTIALS_JSON)
            credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            self.client = gspread.authorize(credentials)
            self.spreadsheet = self.client.open_by_key(self.settings.GOOGLE_SHEET_ID)
            self.is_connected = True
            logger.info("Successfully connected to Google Sheets!")
            self._ensure_sheets_exist()
        except Exception as e:
            logger.warning(f"Failed to connect to Google Sheets ({str(e)}). Falling back to SQLite.")
            self.is_connected = False

    def _ensure_sheets_exist(self):
        """Ensures all 5 required worksheets exist with correct header rows."""
        if not self.is_connected or not self.spreadsheet:
            return

        sheets_schema = {
            "LEADS": LEADS_HEADER,
            "MEDIA_PROFILE": MEDIA_PROFILE_HEADER,
            "OUTREACH": OUTREACH_HEADER,
            "SEARCH_HISTORY": SEARCH_HISTORY_HEADER,
            "ANALYTICS": ANALYTICS_HEADER,
        }

        existing_titles = [ws.title for ws in self.spreadsheet.worksheets()]

        for title, header in sheets_schema.items():
            if title not in existing_titles:
                ws = self.spreadsheet.add_worksheet(title=title, rows=1000, cols=len(header))
                ws.append_row(header)
                logger.info(f"Created sheet '{title}' in Google Sheets.")

    def save_lead(self, lead: Lead) -> bool:
        """Saves lead to both SQLite database and Google Sheets (if connected)."""
        # Save to SQLite first
        self.sqlite_db.insert_or_update_lead(lead)

        if self.is_connected and self.spreadsheet:
            try:
                ws = self.spreadsheet.worksheet("LEADS")
                row = lead.to_sheets_row()
                ws.append_row(row)
                logger.info(f"Saved lead '{lead.business_name}' to Google Sheets.")
            except Exception as e:
                logger.error(f"Error appending lead to Google Sheets: {e}")

        return True

    def sync_media_profile(self, profile: Optional[MediaProfile] = None):
        """Syncs MEDIA_PROFILE to Google Sheets."""
        prof = profile or get_media_profile()
        if self.is_connected and self.spreadsheet:
            try:
                ws = self.spreadsheet.worksheet("MEDIA_PROFILE")
                row = [
                    prof.instagram_handle,
                    prof.followers,
                    prof.monthly_views,
                    prof.audience_country,
                    prof.strong_region,
                    ", ".join(prof.audience_segments),
                    prof.positioning,
                    prof.positioning,
                    prof.contact_email,
                    prof.collaboration_info
                ]
                # Clear and re-populate
                ws.clear()
                ws.append_row(MEDIA_PROFILE_HEADER)
                ws.append_row(row)
            except Exception as e:
                logger.error(f"Failed to sync MEDIA_PROFILE to Google Sheets: {e}")

    def record_search(self, record: SearchHistoryRecord):
        """Records search activity to database and sheets."""
        self.sqlite_db.record_search_history(record)
        if self.is_connected and self.spreadsheet:
            try:
                ws = self.spreadsheet.worksheet("SEARCH_HISTORY")
                ws.append_row(record.to_sheets_row())
            except Exception as e:
                logger.error(f"Error recording search history to Google Sheets: {e}")
