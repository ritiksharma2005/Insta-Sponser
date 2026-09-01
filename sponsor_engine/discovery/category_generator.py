import random
import logging
from typing import List, Dict, Any
from sponsor_engine.database.sqlite_db import SQLiteDatabase
from config.media_profile import get_media_profile

logger = logging.getLogger(__name__)

# Fallback Category Knowledge Base for 70/30 Exploration-Exploitation Strategy
PROVEN_CATEGORIES_POOL = [
    {
        "name": "Coaching & Competitive Exam Institutes",
        "reasoning": "Direct fit for engineering, medical, and GATE/CAT/JEE student audience.",
        "target_audience": "College & aspirant students in India",
        "search_queries": [
            "competitive exam coaching institute Surat",
            "GATE coaching classes Gujarat",
            "coding bootcamp India students",
            "NEET UG coaching center Surat"
        ]
    },
    {
        "name": "Student Housing & PG Services",
        "reasoning": "College students constantly look for hostels, accommodation, and PG rentals.",
        "target_audience": "Outstation students in educational hubs",
        "search_queries": [
            "student PG accommodation Surat",
            "coliving hostel for students Ahmedabad",
            "student housing platform India"
        ]
    },
    {
        "name": "Sports Academies & Fitness Centers",
        "reasoning": "High youth engagement in cricket trials, gym memberships, and sports events.",
        "target_audience": "Youth, sports enthusiasts & college students",
        "search_queries": [
            "cricket academy Surat trials",
            "youth gym fitness club Surat",
            "football academy Gujarat"
        ]
    },
    {
        "name": "EdTech & Career Skill Platforms",
        "reasoning": "Indian students actively seek internships, certifications, and career prep.",
        "target_audience": "Engineering, medical & commerce students",
        "search_queries": [
            "online certification courses Indian students",
            "internship portal India",
            "resume building AI tool students",
            "skill development academy Gujarat"
        ]
    },
    {
        "name": "Laptop Stores & Mobile Repair Services",
        "reasoning": "Essential tech gadget services required by university students.",
        "target_audience": "College students & young tech users",
        "search_queries": [
            "laptop rental for college students Surat",
            "mobile repair store Surat Gujarat",
            "gaming laptop showroom Surat"
        ]
    }
]

EXPERIMENTAL_CATEGORIES_POOL = [
    {
        "name": "AI & SaaS Startups",
        "reasoning": "Engineering & tech-savvy youth are early adopters for AI tools.",
        "target_audience": "Engineering students, tech enthusiasts",
        "search_queries": [
            "AI startup India youth",
            "SaaS productivity tool for students",
            "Indian AI app launch 2026"
        ]
    },
    {
        "name": "Youth D2C Brands & Apparel",
        "reasoning": "Trendy apparel, streetwear, and lifestyle brands target college youth.",
        "target_audience": "College students & young fashion shoppers",
        "search_queries": [
            "D2C streetwear brand India",
            "student fashion footwear Surat",
            "custom merchandise for college events"
        ]
    },
    {
        "name": "Student Travel & Adventure Groups",
        "reasoning": "College students frequently organize weekend trips and treks.",
        "target_audience": "Young travelers & university students",
        "search_queries": [
            "budget student travel agency Gujarat",
            "trekking club Surat youth",
            "college tour organizer India"
        ]
    },
    {
        "name": "Youth Cafes & Student Food Joints",
        "reasoning": "Local cafes and cloud kitchens seeking student footfall and delivery orders.",
        "target_audience": "Local Surat/Gujarat college youth",
        "search_queries": [
            "youth cafe near SVNIT Surat",
            "cloud kitchen student offer Surat",
            "co-working cafe Surat"
        ]
    },
    {
        "name": "Hackathons & Youth Event Platforms",
        "reasoning": "Platforms sponsoring college fests, tech competitions, and cultural events.",
        "target_audience": "College event organizers & participants",
        "search_queries": [
            "national student hackathon sponsor India",
            "college event management company Gujarat",
            "youth festival sponsor India"
        ]
    }
]

class CategoryGenerator:
    """Generates dynamic category discovery lists using 70/30 exploration/exploitation strategy."""

    def __init__(self, db: SQLiteDatabase = None):
        self.db = db or SQLiteDatabase()
        self.media_profile = get_media_profile()

    def generate_categories(self, total_categories: int = 5) -> List[Dict[str, Any]]:
        """
        Generates category list containing 70% proven categories and 30% experimental categories.
        """
        # Determine split
        proven_count = max(1, int(total_categories * 0.7))
        experimental_count = total_categories - proven_count

        # Get performance data from DB
        perf_data = self.db.get_category_performance()

        selected_categories = []

        # 1. Exploitation Phase (Proven categories)
        proven_samples = random.sample(PROVEN_CATEGORIES_POOL, min(proven_count, len(PROVEN_CATEGORIES_POOL)))
        selected_categories.extend(proven_samples)

        # 2. Exploration Phase (New/Experimental categories)
        exp_samples = random.sample(EXPERIMENTAL_CATEGORIES_POOL, min(experimental_count, len(EXPERIMENTAL_CATEGORIES_POOL)))
        selected_categories.extend(exp_samples)

        logger.info(f"Generated {len(selected_categories)} target categories ({proven_count} proven, {experimental_count} experimental)")
        return selected_categories
