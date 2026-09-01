import logging
from datetime import date, timedelta
from typing import Optional
from config.media_profile import get_media_profile
from sponsor_engine.database.models import Lead

logger = logging.getLogger(__name__)

class FollowupScheduler:
    """Schedules and generates concise follow-up messages for contacted sponsors."""

    def __init__(self):
        self.profile = get_media_profile()

    def generate_followup_message(self, lead: Lead, followup_stage: int = 1) -> str:
        """
        Generates shorter, natural follow-up message.
        followup_stage 1: Day 4-7 gentle reminder.
        followup_stage 2: Day 10-14 final follow-up.
        """
        bus_name = lead.business_name

        if followup_stage == 1:
            return (
                f"Hi {bus_name} Team,\n\n"
                f"Following up on my previous note regarding a potential collaboration between {bus_name} and News NIT IIT ({self.profile.instagram_handle}).\n\n"
                f"Would love to know if you'd be open to reviewing our page insights and collaboration options for reaching Indian college youth.\n\n"
                f"Best,\n"
                f"News NIT IIT"
            )
        else:
            return (
                f"Hi {bus_name} Team,\n\n"
                f"One quick final check to see if you might be interested in promoting {bus_name} through News NIT IIT ({self.profile.instagram_handle}).\n\n"
                f"If the timing isn't right now, no worries at all! Feel free to reach out whenever you plan your next campaign.\n\n"
                f"Best regards,\n"
                f"News NIT IIT"
            )

    def calculate_next_followup_date(self, current_stage: int = 0) -> str:
        """Calculates next follow-up date."""
        today = date.today()
        if current_stage == 0:
            next_date = today + timedelta(days=5)
        elif current_stage == 1:
            next_date = today + timedelta(days=7)
        else:
            return "NO_RESPONSE"

        return next_date.isoformat()
