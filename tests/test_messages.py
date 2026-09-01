import pytest
from sponsor_engine.personalization.message_generator import MessageGenerator
from config.media_profile import get_media_profile

def test_message_generator_stats():
    gen = MessageGenerator()
    profile = get_media_profile()

    research_data = {
        "business_name": "ABC Cricket Academy",
        "category": "Sports",
        "city": "Surat",
        "growth_signal": "Upcoming trial registration",
        "description": "Cricket academy in Surat"
    }

    collab_idea = "Promote upcoming cricket trials through Instagram Reels & Story links."
    msg = gen.generate_message(research_data, collab_idea)

    assert "@news.nit_iit" in msg
    assert "2,500+ followers" in msg
    assert "80 lakh+ monthly views" in msg
    assert "ABC Cricket Academy" in msg
    assert "Surat" in msg
