# 05_src/assignment_chat/core/config.py
"""
Final config for Assignment 2 (course API Gateway setup).
"""

from __future__ import annotations

import os
from pathlib import Path

# -------------------------
# App identity / defaults
# -------------------------
APP_NAME = "Toronto City Tour Assistant"
DEFAULT_CITY = "Toronto"

# -------------------------
# Model configuration
# -------------------------
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

# -------------------------
# Course API Gateway config
# -------------------------
BASE_URL = os.getenv(
    "OPENAI_BASE_URL",
    "https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1",
)

# This is the real credential (loaded from .env/.secrets)
API_GATEWAY_KEY = os.getenv("API_GATEWAY_KEY", "")

# -------------------------
# Paths (relative to this file)
# -------------------------
_THIS_DIR = Path(__file__).resolve().parent                 # .../core
_PROJECT_DIR = _THIS_DIR.parent                             # .../assignment_chat

CSV_PATH = str(_PROJECT_DIR / "data" / "toronto_travel_tips.csv")

# Chroma persistence directory (file-based persistence)
CHROMA_DIR = str(_PROJECT_DIR / "db")
COLLECTION_NAME = "toronto_travel_tips"

# -------------------------
# Memory behavior
# -------------------------
MAX_TURNS_IN_CONTEXT = int(os.getenv("MAX_TURNS_IN_CONTEXT", "18"))