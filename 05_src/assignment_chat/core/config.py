import os

APP_NAME = "Toronto City Tour Assistant"
DEFAULT_CITY = "Toronto"

BASE_URL = "https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1"
API_GATEWAY_KEY = os.getenv("API_GATEWAY_KEY")

OPENAI_MODEL = "gpt-4o-mini"
OPENAI_EMBED_MODEL = "text-embedding-3-small"

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "db")
COLLECTION_NAME = "toronto_travel_tips"
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "toronto_travel_tips.csv")

MAX_TURNS_IN_CONTEXT = 18