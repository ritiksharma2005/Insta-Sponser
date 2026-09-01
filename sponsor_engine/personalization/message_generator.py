import logging
from typing import Dict, Any
from config.media_profile import get_media_profile

logger = logging.getLogger(__name__)

class MessageGenerator:
    """Generates personalized, non-spammy collaboration outreach messages for @news.nit_iit."""

    def __init__(self):
        self.profile = get_media_profile()

    def generate_message(
        self,
        research_data: Dict[str, Any],
        suggested_collaboration: str
    ) -> str:
        """
        Creates a custom DM outreach message tailored to the business category and signals.
        """
        bus_name = research_data.get("business_name", "Team")
        city = research_data.get("city", "India")
        category = str(research_data.get("category", "")).lower()
        growth_signal = research_data.get("growth_signal", "")
        description = research_data.get("description", "")

        # 1. Opening & Page Stats Intro (Strictly using MEDIA_PROFILE verified stats)
        intro = (
            f"Hi {bus_name} Team,\n\n"
            f"I'm reaching out from News NIT IIT ({self.profile.instagram_handle}), a student and youth-focused news and information platform "
            f"with {self.profile.followers} followers and {self.profile.monthly_views} monthly views.\n\n"
            f"Our audience is distributed across India, with a strong presence among engineering, medical, and college students and young professionals"
            f"{f' (especially in {self.profile.strong_region})' if 'surat' in city.lower() or 'gujarat' in city.lower() else ''}.\n\n"
        )

        # 2. Specific Business Observation
        observation = ""
        if "coaching" in category or "education" in category:
            observation = f"We came across {bus_name} and noticed your focus on quality competitive coaching and student skill development in {city}. "
        elif "edtech" in category or "skill" in category or "career" in category:
            observation = f"We came across {bus_name} and noticed your platforms designed to equip students with practical skills and career opportunities. "
        elif "sports" in category or "gym" in category:
            observation = f"We came across {bus_name} and noticed your dedication to encouraging sports talent and youth athletic training in {city}. "
        elif "housing" in category or "pg" in category:
            observation = f"We came across {bus_name} and noticed your quality accommodation and hostel services catered for college students in {city}. "
        elif "laptop" in category or "mobile" in category or "electronics" in category:
            observation = f"We came across {bus_name} and noticed your student-friendly tech offerings and gadget services in {city}. "
        elif "ai" in category or "saas" in category or "startup" in category:
            observation = f"We came across {bus_name} and were impressed by your innovative tech solution targeted at young early adopters and tech-savvy students. "
        elif "fashion" in category or "d2c" in category or "apparel" in category:
            observation = f"We came across {bus_name} and really liked your fresh product lineup designed for college lifestyle and youth culture. "
        else:
            observation = f"We came across {bus_name} and noticed your quality services for youth and students in {city}. "

        if growth_signal and growth_signal != "None detected":
            observation += f"We also saw your recent announcement regarding {growth_signal.lower()}. "

        # 3. Collaboration Pitch & Call to Action
        pitch = (
            f"\n\nGiven our student and youth audience, we believe there is a great opportunity to collaborate—for instance, by {suggested_collaboration.lower()}\n\n"
            f"If you're open to exploring a collaboration, I'd be happy to share our detailed page insights and collaboration options.\n\n"
            f"Best regards,\n"
            f"Team News NIT IIT\n"
            f"{self.profile.instagram_handle}"
        )

        message = intro + observation + pitch
        logger.info(f"Generated personalized message for '{bus_name}' ({len(message)} chars)")
        return message
