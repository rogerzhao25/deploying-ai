# 05_src/assignment_chat/core/guardrails.py
"""
Guardrails required by Assignment 2.

This module protects against:
1) Prompt injection / prompt reveal attempts
2) Restricted topics (explicitly required by the assignment):
   - cats / dogs
   - horoscope / zodiac / astrology
   - Taylor Swift

The check_guardrails() function returns:
    (True, "")  -> safe to proceed
    (False, msg)-> block and return msg to user
"""

from __future__ import annotations
import re
from typing import Tuple


# ---------------------------------------------------
# 1) Restricted topics (assignment requirement)
# ---------------------------------------------------
RESTRICTED_TOPICS = [
    r"\bcat(s)?\b",
    r"\bdog(s)?\b",
    r"\bhoroscope(s)?\b",
    r"\bzodiac\b",
    r"\bastrology\b",
    r"\bTaylor\s+Swift\b",
]


# ---------------------------------------------------
# 2) Prompt injection / prompt reveal patterns
# ---------------------------------------------------
PROMPT_ATTACK_PATTERNS = [
    r"system\s*prompt",
    r"reveal.*prompt",
    r"show.*prompt",
    r"print.*prompt",
    r"what.*your.*instructions",
    r"ignore\s+(all|previous)\s+instructions",
    r"override\s+(all|previous)\s+instructions",
    r"change\s+your\s+rules",
    r"modify\s+your\s+rules",
    r"developer\s+message",
    r"hidden\s+instructions",
]


# Friendly responses
RESTRICTED_MSG = (
    "Sorry — I can’t help with that topic. "
    "I’m here to help with Toronto weather, attractions, transit tips, and day-trip planning 🙂"
)

PROMPT_BLOCK_MSG = (
    "I can’t reveal or modify my system instructions, "
    "but I’d be happy to continue helping with your city planning questions!"
)


# ---------------------------------------------------
# Main entry function
# ---------------------------------------------------
def check_guardrails(user_text: str) -> Tuple[bool, str]:
    """
    Returns:
        (True, "") if safe
        (False, message) if blocked
    """
    if not user_text:
        return True, ""

    text = user_text.strip()

    # --- Restricted topics ---
    for pattern in RESTRICTED_TOPICS:
        if re.search(pattern, text, re.IGNORECASE):
            return False, RESTRICTED_MSG

    # --- Prompt injection / prompt reveal ---
    for pattern in PROMPT_ATTACK_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return False, PROMPT_BLOCK_MSG

    return True, ""
