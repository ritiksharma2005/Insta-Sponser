import re
from typing import Dict, Any, Tuple

def normalize_instagram_handle(handle: str) -> str:
    """Standardizes Instagram handle format with '@' prefix."""
    if not handle or handle.strip() in ("Not Available", "None", ""):
        return "Not Available"

    clean = handle.strip()
    # If URL, extract path component
    if "instagram.com" in clean:
        match = re.search(r"instagram\.com/([a-zA-Z0-9_\.\-]+)", clean)
        if match:
            clean = match.group(1)
    
    clean = clean.lstrip("@").rstrip("/")
    return f"@{clean}" if clean else "Not Available"

def normalize_url(url: str) -> str:
    """Standardizes web URLs."""
    if not url or url.strip() in ("Not Available", "None", ""):
        return "Not Available"
    
    clean = url.strip()
    if not clean.startswith(("http://", "https://")):
        clean = f"https://{clean}"
    return clean

def validate_lead_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """Validates raw lead data before database insertion."""
    business_name = data.get("business_name")
    if not business_name or str(business_name).strip() == "":
        return False, "Missing business name"

    score = data.get("lead_score", 50)
    if not isinstance(score, int) or score < 0 or score > 100:
        return False, f"Invalid lead score: {score}"

    return True, "Valid"
