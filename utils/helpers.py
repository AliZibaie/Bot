import re


def extract_url(text: str) -> str | None:
    """Extract the first URL from a string."""
    match = re.search(r"https?://\S+", text)
    return match.group(0) if match else None


def truncate(text: str, max_length: int = 200) -> str:
    """Truncate text to max_length, appending ellipsis if needed."""
    return text if len(text) <= max_length else text[:max_length] + "…"
