import pytest
from sponsor_engine.utils.validation import normalize_instagram_handle, normalize_url, validate_lead_data

def test_normalize_instagram_handle():
    assert normalize_instagram_handle("news.nit_iit") == "@news.nit_iit"
    assert normalize_instagram_handle("@news.nit_iit") == "@news.nit_iit"
    assert normalize_instagram_handle("https://instagram.com/news.nit_iit/") == "@news.nit_iit"
    assert normalize_instagram_handle("Not Available") == "Not Available"

def test_normalize_url():
    assert normalize_url("example.com") == "https://example.com"
    assert normalize_url("http://example.com") == "http://example.com"
    assert normalize_url("Not Available") == "Not Available"

def test_validate_lead_data():
    valid, msg = validate_lead_data({"business_name": "ABC Corp", "lead_score": 85})
    assert valid is True

    invalid, err_msg = validate_lead_data({"business_name": "", "lead_score": 85})
    assert invalid is False
    assert "Missing business name" in err_msg
