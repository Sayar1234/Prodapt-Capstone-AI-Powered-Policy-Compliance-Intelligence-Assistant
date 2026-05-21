BLOCKED_PHRASES = ["ignore previous instructions", "reveal system prompt", "exfiltrate"]


def screen_user_text(text: str) -> tuple[bool, list[str]]:
    lowered = text.lower()
    hits = [phrase for phrase in BLOCKED_PHRASES if phrase in lowered]
    return len(hits) == 0, hits
