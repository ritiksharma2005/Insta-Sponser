import pytest
import sqlite3
from pathlib import Path
from sponsor_engine.database.sqlite_db import SQLiteDatabase
from sponsor_engine.database.models import Lead
from sponsor_engine.utils.deduplication import DeduplicationEngine

def test_deduplication_engine(tmp_path: Path):
    db_file = tmp_path / "test_engine.db"
    db = SQLiteDatabase(db_path=db_file)
    dedup = DeduplicationEngine(db=db)

    # Insert initial lead
    lead1 = Lead(
        lead_id="LEAD-TEST-001",
        business_name="Pro Cricket Surat",
        instagram="@procricket_surat",
        website="https://procricketsurat.in",
        email="info@procricketsurat.in",
        phone="9876543210"
    )
    db.insert_or_update_lead(lead1)

    # Test duplicate by Instagram
    is_dup, match = dedup.is_duplicate(instagram="procricket_surat")
    assert is_dup is True
    assert match.lead_id == "LEAD-TEST-001"

    # Test duplicate by website
    is_dup_web, match_web = dedup.is_duplicate(website="https://procricketsurat.in")
    assert is_dup_web is True

    # Test non-duplicate
    is_dup_new, match_new = dedup.is_duplicate(instagram="@new_academy_xyz")
    assert is_dup_new is False
    assert match_new is None
