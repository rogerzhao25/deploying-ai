import re

RESTRICTED_TOPICS = [
    r"\bcat(s)?\b", r"\bdog(s)?\b",
    r"\bhoroscope(s)?\b", r"\bzodiac\b", r"\bastrology\b",
    r"\bTaylor\s+Swift\b",
]

PROMPT_ATTACK_PATTERNS = [
    r"system prompt", r"reveal.*prompt", r"show.*prompt",
    r"ignore (all|previous) instructions", r"override.*system",
]

def check_guardrails(user_text: str):
    for pat in RESTRICTED_TOPICS:
        if re.search(pat, user_text, re.IGNORECASE):
            return False, "Sorry, I cannot answer questions about cats/dogs, horoscopes/zodiac, or Taylor Swift."

    for pat in PROMPT_ATTACK_PATTERNS:
        if re.search(pat, user_text, re.IGNORECASE):
            return False, "I cannot reveal or modify the system prompt."

    return True, ""
