import sqlite3
import json
from typing import List, Optional, Dict, Any
from pathlib import Path
from config.settings import get_settings
from sponsor_engine.database.models import Lead, SearchHistoryRecord, OutreachRecord

class SQLiteDatabase:
    """Local SQLite database manager for offline execution and lead persistence."""

    def __init__(self, db_path: Optional[Path] = None):
        settings = get_settings()
        self.db_path = db_path or settings.SQLITE_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes database schema if tables do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Leads Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    lead_id TEXT PRIMARY KEY,
                    date_found TEXT,
                    business_name TEXT,
                    category TEXT,
                    subcategory TEXT,
                    city TEXT,
                    state TEXT,
                    country TEXT,
                    website TEXT,
                    instagram TEXT,
                    followers TEXT,
                    linkedin TEXT,
                    email TEXT,
                    phone TEXT,
                    description TEXT,
                    target_audience TEXT,
                    student_relevance TEXT,
                    youth_relevance TEXT,
                    geographic_relevance TEXT,
                    social_activity TEXT,
                    growth_signal TEXT,
                    discovery_source TEXT,
                    research_date TEXT,
                    lead_score INTEGER,
                    lead_tier TEXT,
                    why_suitable TEXT,
                    suggested_collaboration TEXT,
                    personalized_message TEXT,
                    status TEXT,
                    last_contacted TEXT,
                    next_followup TEXT,
                    response TEXT,
                    notes TEXT
                )
            """)

            # Search History Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    category TEXT,
                    keyword TEXT,
                    location TEXT,
                    source TEXT,
                    candidates_found INTEGER,
                    qualified_leads INTEGER,
                    rejected_leads INTEGER
                )
            """)

            # Outreach Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS outreach (
                    lead_id TEXT PRIMARY KEY,
                    business TEXT,
                    message TEXT,
                    generated_date TEXT,
                    approved INTEGER,
                    sent_date TEXT,
                    response TEXT,
                    followup_date TEXT,
                    status TEXT
                )
            """)

            # Media Profile Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS media_profile (
                    id INTEGER PRIMARY KEY DEFAULT 1,
                    data_json TEXT
                )
            """)

            # Category Performance Learning Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS category_performance (
                    category TEXT PRIMARY KEY,
                    total_discovered INTEGER DEFAULT 0,
                    qualified_leads INTEGER DEFAULT 0,
                    approved_leads INTEGER DEFAULT 0,
                    replies INTEGER DEFAULT 0,
                    conversions INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    def insert_or_update_lead(self, lead: Lead) -> bool:
        """Inserts a new lead or updates existing record."""
        row_data = lead.model_dump()
        fields = list(row_data.keys())
        placeholders = ", ".join(["?"] * len(fields))
        update_clause = ", ".join([f"{k}=excluded.{k}" for k in fields if k != "lead_id"])

        query = f"""
            INSERT INTO leads ({", ".join(fields)})
            VALUES ({placeholders})
            ON CONFLICT(lead_id) DO UPDATE SET {update_clause}
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, list(row_data.values()))
            conn.commit()
            return True

    def get_all_leads(self) -> List[Lead]:
        """Fetches all stored leads."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM leads ORDER BY lead_score DESC")
            rows = cursor.fetchall()
            return [Lead(**dict(row)) for row in rows]

    def get_lead_by_id(self, lead_id: str) -> Optional[Lead]:
        """Fetch lead by lead_id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM leads WHERE lead_id = ?", (lead_id,))
            row = cursor.fetchone()
            return Lead(**dict(row)) if row else None

    def find_duplicate_lead(self, instagram: str, website: str, business_name: str, email: str, phone: str) -> Optional[Lead]:
        """Checks for existing duplicate lead across unique identifiers."""
        conditions = []
        params = []

        if instagram and instagram != "Not Available":
            clean_ig = instagram.strip().lstrip("@").lower()
            conditions.append("LOWER(REPLACE(instagram, '@', '')) = ?")
            params.append(clean_ig)
        if website and website != "Not Available":
            clean_web = website.strip().lower().replace("https://", "").replace("http://", "").rstrip("/")
            conditions.append("LOWER(website) LIKE ?")
            params.append(f"%{clean_web}%")
        if business_name:
            conditions.append("LOWER(business_name) = ?")
            params.append(business_name.strip().lower())
        if email and email != "Not Available":
            conditions.append("LOWER(email) = ?")
            params.append(email.strip().lower())
        if phone and phone != "Not Available":
            conditions.append("phone = ?")
            params.append(phone.strip())

        if not conditions:
            return None

        query = f"SELECT * FROM leads WHERE {" OR ".join(conditions)} LIMIT 1"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return Lead(**dict(row)) if row else None

    def update_lead_status(self, lead_id: str, new_status: str, notes: str = ""):
        """Update lead status and optional notes."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE leads SET status = ?, notes = CASE WHEN ? != '' THEN ? ELSE notes END WHERE lead_id = ?",
                (new_status, notes, notes, lead_id)
            )
            conn.commit()

    def record_search_history(self, record: SearchHistoryRecord):
        """Saves search execution details."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO search_history (date, category, keyword, location, source, candidates_found, qualified_leads, rejected_leads)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (record.date, record.category, record.keyword, record.location, record.source, record.candidates_found, record.qualified_leads, record.rejected_leads))
            
            # Also update category performance tracker
            cursor.execute("""
                INSERT INTO category_performance (category, total_discovered, qualified_leads)
                VALUES (?, ?, ?)
                ON CONFLICT(category) DO UPDATE SET
                    total_discovered = total_discovered + excluded.total_discovered,
                    qualified_leads = qualified_leads + excluded.qualified_leads
            """, (record.category, record.candidates_found, record.qualified_leads))
            conn.commit()

    def get_category_performance(self) -> List[Dict[str, Any]]:
        """Fetch category performance metrics for AI exploration/exploitation strategy."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM category_performance ORDER BY qualified_leads DESC")
            return [dict(row) for row in cursor.fetchall()]
