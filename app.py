import uuid
from pathlib import Path

import pandas as pd
import streamlit as st

from config import DEFAULT_CITY, USE_MOCK_DATA
from database import (
    create_tables,
    create_user,
    delete_user,
    ensure_schema,
    get_all_users,
    get_or_create_place,
    get_user_history,
    log_visit,
    seed_users,
)
from mood_logic import COMPANIONS, MOOD_DEFAULTS
from recommender import recommend_places

DB_PATH = Path(__file__).parent / "moodmap.db"
UPLOADS_DIR = Path(__file__).parent / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)
MAX_CARDS_SHOWN = 12

st.set_page_config(page_title="MoodMap", page_icon="🧭", layout="centered")

if not DB_PATH.exists():
    create_tables()
ensure_schema()

users = get_all_users()
if not users:
    seed_users()
    users = get_all_users()

st.title("🧭 MoodMap")
st.caption("Tell us your mood, we'll tell you where to go.")

if USE_MOCK_DATA:
    st.info(
        "No Google Places API key configured — showing mock place data. "
        "Add `GOOGLE_PLACES_API_KEY` to a `.env` file to use live results.",
        icon="ℹ️",
    )

usernames = [u[1] for u in users]

with st.sidebar:
    st.subheader("Who's asking?")
    if usernames:
        selected = st.session_state.get("selected_username")
        default_idx = usernames.index(selected) if selected in usernames else 0
        username = st.selectbox("User", usernames, index=default_idx)
        st.session_state["selected_username"] = username

        if st.session_state.get("confirm_delete") == username:
            st.warning(f"Delete **{username}** and all their visit history? This can't be undone.")
            c1, c2 = st.columns(2)
            if c1.button("Yes, delete", key="confirm_delete_yes"):
                user_id = next(u[0] for u in users if u[1] == username)
                delete_user(user_id)
                st.session_state.pop("confirm_delete", None)
                st.session_state.pop("selected_username", None)
                st.rerun()
            if c2.button("Cancel", key="confirm_delete_no"):
                st.session_state.pop("confirm_delete", None)
                st.rerun()
        elif st.button("Delete this user", key="delete_user_btn"):
            st.session_state["confirm_delete"] = username
            st.rerun()
    else:
        username = None

    with st.expander("+ New user"):
        new_name = st.text_input("Name", key="new_user_name")
        new_city = st.text_input("City", value=DEFAULT_CITY, key="new_user_city")
        if st.button("Create user"):
            name = new_name.strip()
            if name:
                create_user(name, new_city.strip() or DEFAULT_CITY)
                st.session_state["selected_username"] = name
                st.rerun()
            else:
                st.warning("Enter a name first.")

    if username:
        st.divider()
        st.subheader(f"{username}'s visit history")
        history = get_user_history(next(u[0] for u in users if u[1] == username))
        if history:
            for place_name, category, visit_mood, visit_companion, visited_at, photo_path in history:
                cols = st.columns([1, 3]) if photo_path else [None, st]
                if photo_path and Path(photo_path).exists():
                    cols[0].image(photo_path, width=60)
                target = cols[1]
                target.markdown(f"**{place_name}**")
                target.caption(f"{visit_mood} · {visit_companion} · {visited_at}")
        else:
            st.caption("No visits logged yet.")

moods = sorted(MOOD_DEFAULTS.keys())
companions = COMPANIONS

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
    if len(places) > MAX_CARDS_SHOWN:
        st.caption(f"Showing top {MAX_CARDS_SHOWN} of {len(places)} results.")

    for place in places[:MAX_CARDS_SHOWN]:
        with st.container(border=True):
            if place.get("photo_url"):
                st.image(place["photo_url"], width=300)
            c1, c2 = st.columns([3, 1])
            c1.markdown(f"**{place['name']}**  \n{place['category'].replace('_', ' ').title()}")
            c2.metric("Rating", place.get("rating", "—"))

            if username:
                photo = st.file_uploader(
                    "Add a photo (optional)",
                    type=["png", "jpg", "jpeg"],
                    key=f"photo-{place['google_place_id']}",
                    label_visibility="collapsed",
                )
                if st.button("Log visit", key=f"visit-{place['google_place_id']}"):
                    photo_path = None
                    if photo is not None:
                        ext = Path(photo.name).suffix or ".jpg"
                        photo_path = str(UPLOADS_DIR / f"{uuid.uuid4().hex}{ext}")
                        with open(photo_path, "wb") as f:
                            f.write(photo.getbuffer())
                    place_id = get_or_create_place(place)
                    user_id = next(u[0] for u in users if u[1] == username)
                    log_visit(user_id, place_id, q_mood, q_companion, photo_path)
                    st.success(f"Logged a visit to {place['name']}")

    map_df = pd.DataFrame(
        [{"lat": p["latitude"], "lon": p["longitude"]} for p in places if p.get("latitude")]
    )
    if not map_df.empty:
        st.map(map_df)
