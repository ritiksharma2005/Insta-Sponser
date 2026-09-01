import re
import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class WebsiteResearcher:
    """Extracts public business details, contact email/phone, and growth signals from websites."""

    def research_website(self, website_url: str, snippet: str = "") -> Dict[str, Any]:
        """Extracts contact info, description, and growth signals safely."""
        result = {
            "email": "Not Available",
            "phone": "Not Available",
            "description": snippet if snippet else "Not Available",
            "growth_signal": "None detected"
        }

        if not website_url or website_url == "Not Available":
            return result

        # Check for growth signal keywords in snippet
        growth_keywords = {
            "trial": "Upcoming sports/trial announcement",
            "hiring": "Active hiring / Internship campaign",
            "launch": "New product/service launch",
            "batch": "New admission/coaching batch",
            "opening": "New branch expansion",
            "fest": "College fest / Event sponsorship"
        }

        found_signals = []
        low_snippet = snippet.lower()
        for kw, signal_desc in growth_keywords.items():
            if kw in low_snippet:
                found_signals.append(signal_desc)

        if found_signals:
            result["growth_signal"] = "; ".join(found_signals)

        # Look for email patterns in snippet
        email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", snippet)
        if email_match:
            result["email"] = email_match.group(0)

        # Look for phone patterns
        phone_match = re.search(r"(\+91[\s-]?)?[6-9]\d{9}", snippet)
        if phone_match:
            result["phone"] = phone_match.group(0)

        return result
