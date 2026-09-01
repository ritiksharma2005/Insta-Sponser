import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class InstagramResearcher:
    """Extracts public Instagram information safely without bypassing security controls."""

    def research_profile(self, instagram_handle: str, snippet: str = "") -> Dict[str, Any]:
        """Returns public metrics or 'Not Available' if profile data is restricted."""
        clean_handle = instagram_handle.strip()
        if not clean_handle.startswith("@") and clean_handle != "Not Available":
            clean_handle = f"@{clean_handle.lstrip('@')}"

        # Look for follower hints in search snippet if available
        followers = "Not Available"
        if snippet:
            match = re.search(r"([\d\.,kKmM]+)\s+followers", snippet, re.IGNORECASE)
            if match:
                followers = match.group(1)

        return {
            "instagram_handle": clean_handle if clean_handle else "Not Available",
            "followers": followers,
            "social_activity": "Active public profile" if clean_handle != "Not Available" else "Not Available"
        }
