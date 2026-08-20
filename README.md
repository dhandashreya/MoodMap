# MoodMap

Pick a mood and who you're with, and MoodMap suggests places in your city to go — then lets you log the visit and build a history.

## How it works

| Component | Description |
|---|---|
| `mood_logic.py` | Maps a (mood, companion) pair to Google Places types, e.g. `("Low Energy + Cozy", "Solo")` → `["cafe", "book_store"]` |
| `api_utils.py` | Looks up places for those types. Uses the Google Places API if a key is configured, otherwise falls back to mock Edmonton place data |
| `recommender.py` | Combines the two above and ranks results by rating |
| `database.py` | SQLite storage for users, places, visits, and reviews |
| `app.py` | Streamlit UI — pick a mood, get recommendations, log visits |

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
python database.py            # creates moodmap.db and seeds sample users
```

## Using a real Google Places API key (optional)

Without a key, the app shows mock Edmonton place data so it's usable out of the box. To use live results:

1. Create an API key for the [Places API](https://developers.google.com/maps/documentation/places/web-service/overview) in Google Cloud (billing must be enabled).
2. Copy `.env.example` to `.env` and paste your key in:
   ```
   GOOGLE_PLACES_API_KEY=your_key_here
   ```
3. Restart the app — it automatically switches from mock to live data when a key is present.

## Run

```bash
streamlit run app.py
```

Opens at `http://localhost:8501`. Pick a mood and companion, click **Find places**, and optionally log a visit if you've selected a user in the sidebar.
