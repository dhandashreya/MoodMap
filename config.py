import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent

GOOGLE_PLACES_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
USE_MOCK_DATA = not GOOGLE_PLACES_API_KEY

DEFAULT_CITY = "Edmonton"
CITY_COORDS = {
    "Edmonton": (53.5461, -113.4938),
}
