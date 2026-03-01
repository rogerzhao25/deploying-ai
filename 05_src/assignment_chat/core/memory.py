# 05_src/assignment_chat/core/memory.py
"""
Simple session memory for Assignment 2.

We store:
1) Short-term chat history (for conversational continuity)
2) Lightweight user preferences (bonus points in assignment):
   - budget (low / medium / high)
   - with_kids (true)
   - indoor_preference (true / false)

This memory lives only for the current Gradio session.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class SessionMemory:
    # Structured preferences extracted from conversation
    prefs: Dict[str, str] = field(default_factory=dict)

    # Chat history: [{"role":"user|assistant","content":"..."}]
    messages: List[Dict[str, str]] = field(default_factory=list)

    # -----------------------------------------------------
    # Preference extraction (very simple keyword matching)
    # -----------------------------------------------------
    def update_prefs_from_text(self, text: str) -> None:
        if not text:
            return

        t = text.lower()

        # Budget detection
        if "budget low" in t or "cheap" in t or "low budget" in t:
            self.prefs["budget"] = "low"

        elif "budget medium" in t or "mid budget" in t:
            self.prefs["budget"] = "medium"

        elif "budget high" in t or "luxury" in t or "high budget" in t:
            self.prefs["budget"] = "high"

        # Family / kids detection
        if "with kids" in t or "with children" in t or "family trip" in t:
            self.prefs["with_kids"] = "true"

        # Indoor / outdoor preference
        if "indoor" in t:
            self.prefs["indoor_preference"] = "true"

        if "outdoor" in t:
            self.prefs["indoor_preference"] = "false"

    # -----------------------------------------------------
    # Chat history helpers
    # -----------------------------------------------------
    def add(self, role: str, content: str) -> None:
        """Append a message to chat history."""
        self.messages.append({"role": role, "content": content})

    def trim(self, max_turns: int) -> None:
        """
        Keep only the last N turns to avoid long context.
        1 turn ≈ user + assistant → ~2 messages.
        """
        max_msgs = max_turns * 2
        if len(self.messages) > max_msgs:
            self.messages = self.messages[-max_msgs:]

    def summary(self) -> str:
        """Return a readable summary of stored preferences."""
        if not self.prefs:
            return "No stored preferences yet."
        return ", ".join(f"{k}={v}" for k, v in self.prefs.items())
