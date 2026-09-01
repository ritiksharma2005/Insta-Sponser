import pytest
from sponsor_engine.scoring.lead_scorer import LeadScorer

def test_lead_scorer_hot_tier():
    scorer = LeadScorer()
    high_lead_data = {
        "business_name": "Surat Cricket Academy",
        "category": "Sports Academies & Fitness Centers",
        "city": "Surat",
        "student_relevance": "Direct target audience alignment",
        "youth_relevance": "Very High",
        "website": "https://suratcricket.in",
        "email": "contact@suratcricket.in",
        "instagram": "@suratcricket",
        "geographic_relevance": "Surat/Gujarat regional hub",
        "growth_signal": "Upcoming trials announcement"
    }

    score, tier, why_suitable = scorer.evaluate_lead(high_lead_data)
    assert score >= 75
    assert tier in ("HOT", "HIGH")
    assert "Surat Cricket Academy" in why_suitable

def test_lead_scorer_medium_tier():
    scorer = LeadScorer()
    med_lead_data = {
        "business_name": "General Stationary Hub",
        "category": "Stationery",
        "city": "Jaipur",
        "student_relevance": "Basic youth relevance",
        "youth_relevance": "Medium",
        "website": "Not Available",
        "email": "Not Available",
        "instagram": "Not Available",
        "geographic_relevance": "National",
        "growth_signal": "None detected"
    }

    score, tier, _ = scorer.evaluate_lead(med_lead_data)
    assert score < 75
    assert tier in ("MEDIUM", "LOW")
