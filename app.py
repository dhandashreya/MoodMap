from pathlib import Path

import pandas as pd
import streamlit as st

from config import DEFAULT_CITY, USE_MOCK_DATA
from database import create_tables, get_all_users, get_or_create_place, get_user_history, log_visit
from mood_logic import MOOD_MAP
from recommender import recommend_places

DB_PATH = Path(__file__).parent / "moodmap.db"

st.set_page_config(page_title="MoodMap", page_icon="🧭", layout="centered")

if not DB_PATH.exists():
    create_tables()

st.title("🧭 MoodMap")
st.caption("Tell us your mood, we'll tell you where to go.")

if USE_MOCK_DATA:
    st.info(
        "No Google Places API key configured — showing mock place data. "
        "Add `GOOGLE_PLACES_API_KEY` to a `.env` file to use live results.",
        icon="ℹ️",
    )

users = get_all_users()
usernames = [u[1] for u in users]

with st.sidebar:
    st.subheader("Who's asking?")
    if usernames:
        username = st.selectbox("User", usernames)
    else:
        username = None
        st.warning("No users yet. Run `python database.py` to seed sample users.")

moods = sorted({mood for mood, _ in MOOD_MAP.keys()})
companions = sorted({companion for _, companion in MOOD_MAP.keys()})

col1, col2 = st.columns(2)
mood = col1.selectbox("Mood", moods)
companion = col2.selectbox("Who's with you?", companions)
city = st.text_input("City", value=DEFAULT_CITY)

if st.button("Find places", type="primary"):
    st.session_state["places"] = recommend_places(mood, companion, city)
    st.session_state["last_query"] = (mood, companion)

places = st.session_state.get("places")

if places == []:
    st.warning("No place types are mapped for that mood + companion combination yet.")
elif places:
    q_mood, q_companion = st.session_state["last_query"]
    st.subheader(f"Recommended for {q_mood} with {q_companion}")

    for place in places:
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"**{place['name']}**  \n{place['category'].replace('_', ' ').title()}")
            c2.metric("Rating", place.get("rating", "—"))
            if username and st.button("Log visit", key=f"visit-{place['google_place_id']}"):
                place_id = get_or_create_place(place)
                user_id = next(u[0] for u in users if u[1] == username)
                log_visit(user_id, place_id, q_mood, q_companion)
                st.success(f"Logged a visit to {place['name']}")

    map_df = pd.DataFrame(
        [{"lat": p["latitude"], "lon": p["longitude"]} for p in places if p.get("latitude")]
    )
    if not map_df.empty:
        st.map(map_df)

if username:
    st.divider()
    st.subheader(f"{username}'s visit history")
    history = get_user_history(next(u[0] for u in users if u[1] == username))
    if history:
        st.table(
            pd.DataFrame(
                history, columns=["Place", "Category", "Mood", "Companion", "Visited"]
            )
        )
    else:
        st.caption("No visits logged yet.")
