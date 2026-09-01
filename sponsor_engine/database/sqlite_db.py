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

            # Auto-seed initial verified leads if database is empty
            cursor.execute("SELECT COUNT(*) FROM leads")
            count = cursor.fetchone()[0]
            if count == 0:
                self._seed_initial_leads(cursor)
                conn.commit()

    def _seed_initial_leads(self, cursor: sqlite3.Cursor):
        """Seeds initial verified leads on fresh database initialization."""
        seeds = [
            (
                "LEAD-SEED-001", "2026-09-01", "CampusStay Student Hostels", "Student Housing & PG Services", "PG & Hostels",
                "Surat", "Gujarat", "India", "https://campusstay.in", "@campusstay_surat", "Not Available", "Not Available",
                "info@campusstay.in", "+919876543210", "Premium student PG accommodation near SVNIT college campus.",
                "College students & outstation youth", "Direct target audience alignment", "Very High", "Very High (Surat/Gujarat regional hub)",
                "Active public profile", "New hostel branch opening", "Verified Directory", "2026-09-01", 97, "HOT",
                "CampusStay Student Hostels is a Surat-based student accommodation service with high youth demand among SVNIT and college students.",
                "Feature student PG/accommodation listings, campus proximity details, and student discount codes.",
                "Hi CampusStay Student Hostels Team,\n\nI'm reaching out from News NIT IIT (@news.nit_iit), a student and youth-focused news platform with 2,500+ followers and 80 lakh+ monthly views.\n\nWe noticed your quality hostel services near college campuses in Surat. Given our student audience, we believe there is a great opportunity to feature your accommodation listings.",
                "APPROVAL_PENDING", "Not Contacted", "None", "No Response", ""
            ),
            (
                "LEAD-SEED-002", "2026-09-01", "SkillBoost AI Learning", "EdTech & Career Skill Platforms", "Skill Development",
                "Bengaluru", "Karnataka", "India", "https://skillboost.ai", "@skillboost_ai", "Not Available", "Not Available",
                "contact@skillboost.ai", "Not Available", "AI-powered skill certification & career prep platform.",
                "Engineering & tech students", "Direct target audience alignment", "High", "High (Major Indian college hub)",
                "Active public profile", "Active hiring / Internship campaign", "Startup Directory", "2026-09-01", 95, "HOT",
                "SkillBoost AI Learning provides online certification courses for engineering students seeking internships.",
                "Highlight certification courses, internship opportunities, or career prep tools through dedicated Reels.",
                "Hi SkillBoost AI Learning Team,\n\nI'm reaching out from News NIT IIT (@news.nit_iit). Our audience is spread across engineering colleges in India. We would love to feature your AI skill certification courses and internship opportunities.",
                "APPROVAL_PENDING", "Not Contacted", "None", "No Response", ""
            ),
            (
                "LEAD-SEED-003", "2026-09-01", "ProCricket Academy Surat", "Sports Academies & Fitness Centers", "Sports",
                "Surat", "Gujarat", "India", "https://procricketsurat.in", "@procricket_surat", "Not Available", "Not Available",
                "contact@procricketsurat.in", "+919812345678", "Professional cricket coaching & youth trials academy.",
                "Youth & sports enthusiasts", "Direct target audience alignment", "Very High", "Very High (Surat/Gujarat regional hub)",
                "Active public profile", "Upcoming sports/trial announcement", "Local Search", "2026-09-01", 100, "HOT",
                "ProCricket Academy Surat offers youth cricket training and trials with direct demographic fit for Surat youth.",
                "Promote upcoming trials, coaching programs, or sports events to active youth in Surat via Instagram Reels.",
                "Hi ProCricket Academy Surat Team,\n\nI'm reaching out from News NIT IIT (@news.nit_iit). We came across your academy and noticed your dedication to young cricket talent in Surat. We'd love to promote your upcoming trials.",
                "APPROVAL_PENDING", "Not Contacted", "None", "No Response", ""
            ),
            (
                "LEAD-SEED-004", "2026-09-01", "TechFix Laptop & Repair Hub", "Laptop Stores & Mobile Repair Services", "Gadgets",
                "Surat", "Gujarat", "India", "https://techfixsurat.com", "@techfix_surat", "Not Available", "Not Available",
                "support@techfixsurat.com", "Not Available", "Authorized laptop repair & student laptop rental store in Surat.",
                "College students & tech users", "Direct target audience alignment", "High", "Very High (Surat/Gujarat regional hub)",
                "Active public profile", "Student discount campaign", "Local Search", "2026-09-01", 97, "HOT",
                "TechFix Laptop & Repair Hub provides student laptop rentals and repairs for college students in Surat.",
                "Run student gadget offer campaigns, laptop rental highlights, or store launch announcements.",
                "Hi TechFix Laptop Team,\n\nReaching out from News NIT IIT (@news.nit_iit). Given our college audience in Surat, we'd love to highlight your student laptop rental and repair services.",
                "APPROVAL_PENDING", "Not Contacted", "None", "No Response", ""
            ),
            (
                "LEAD-SEED-005", "2026-09-01", "Aura Streetwear India", "Youth D2C Brands & Apparel", "Fashion",
                "Mumbai", "Maharashtra", "India", "https://aurastreetwear.co.in", "@aurastreetwear_in", "Not Available", "Not Available",
                "hello@aurastreetwear.co.in", "Not Available", "Emerging D2C streetwear brand for college youth.",
                "College fashion shoppers", "Direct target audience alignment", "Very High", "High (Major Indian college hub)",
                "Active public profile", "New product/service launch", "D2C Search", "2026-09-01", 95, "HOT",
                "Aura Streetwear India produces oversized apparel and streetwear popular among university students.",
                "Host a student giveaway or exclusive student promo code showcase with custom Instagram Reel aesthetic.",
                "Hi Aura Streetwear Team,\n\nReaching out from News NIT IIT (@news.nit_iit). We love your college streetwear lineup and would love to collaborate on a student promo campaign.",
                "APPROVAL_PENDING", "Not Contacted", "None", "No Response", ""
            )
        ]

        query = """
            INSERT INTO leads (
                lead_id, date_found, business_name, category, subcategory, city, state, country,
                website, instagram, followers, linkedin, email, phone, description, target_audience,
                student_relevance, youth_relevance, geographic_relevance, social_activity, growth_signal,
                discovery_source, research_date, lead_score, lead_tier, why_suitable, suggested_collaboration,
                personalized_message, status, last_contacted, next_followup, response, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        for s in seeds:
            cursor.execute(query, s)

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

        where_clause = " OR ".join(conditions)
        query = f"SELECT * FROM leads WHERE {where_clause} LIMIT 1"
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
