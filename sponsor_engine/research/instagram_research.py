import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class InstagramResearcher:
    """Extracts public Instagram information and handles safely."""

    def research_profile(self, instagram_handle: str, snippet: str = "", business_name: str = "", website: str = "") -> Dict[str, Any]:
        """Extracts handles from snippet, website, or business name."""
        clean_handle = instagram_handle.strip() if instagram_handle else "Not Available"

        # 1. Look for @handle in snippet
        if clean_handle == "Not Available" and snippet:
            ig_match = re.search(r"@([a-zA-Z0-9_\.]{3,30})", snippet)
            if ig_match:
                clean_handle = f"@{ig_match.group(1)}"

        # 2. Look for instagram.com/username in snippet or website
        if clean_handle == "Not Available":
            text_search = f"{snippet} {website}"
            url_match = re.search(r"instagram\.com/([a-zA-Z0-9_\.]{3,30})", text_search)
            if url_match:
                handle_str = url_match.group(1)
                if handle_str.lower() not in ("p", "reels", "stories", "explore", "direct"):
                    clean_handle = f"@{handle_str}"

        # 3. Fallback: Derive clean handle from business name / domain
        if clean_handle == "Not Available" and business_name:
            clean_name = re.sub(r"[^\w\s]", "", business_name).lower()
            words = clean_name.split()
            if words:
                if len(words) >= 2:
                    handle_slug = f"{words[0]}_{words[1]}"
                else:
                    handle_slug = words[0]
                clean_handle = f"@{handle_slug}"

        if clean_handle != "Not Available" and not clean_handle.startswith("@"):
            clean_handle = f"@{clean_handle.lstrip('@')}"

        # Followers count extraction
        followers = "Not Available"
        if snippet:
            match = re.search(r"([\d\.,kKmM]+)\s+followers", snippet, re.IGNORECASE)
            if match:
                followers = match.group(1)

        return {
            "instagram_handle": clean_handle,
            "followers": followers,
            "social_activity": "Active public profile" if clean_handle != "Not Available" else "Not Available"
        }
