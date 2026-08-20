import random

import requests

from config import CITY_COORDS, DEFAULT_CITY, GOOGLE_PLACES_API_KEY, USE_MOCK_DATA

TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"

# Real-looking Edmonton place names so mock mode is usable without an API key.
_MOCK_NAMES = {
    "restaurant": ["The Marc", "Characters Fine Dining", "Kanto Modern Filipino", "Meat by RGE RD"],
    "cafe": ["Credo Coffee", "Transcend Coffee", "Duchess Bake Shop", "Remedy Café"],
    "art_gallery": ["Art Gallery of Alberta", "The Front Gallery", "SNAP Gallery"],
    "amusement_park": ["Galaxyland", "World Waterpark"],
    "tourist_attraction": ["West Edmonton Mall", "Muttart Conservatory", "Fort Edmonton Park"],
    "book_store": ["Audreys Books", "Wee Book Inn", "Glass Bookshop"],
    "park": ["William Hawrelak Park", "River Valley Trail", "Queen Elizabeth Park"],
    "bowling_alley": ["Metro Bowl", "Ferrari's Bowling Lounge"],
    "movie_theater": ["Landmark Cinemas City Centre", "Metro Cinema"],
    "museum": ["Royal Alberta Museum", "TELUS World of Science"],
}


def _mock_search(place_type, city):
    names = _MOCK_NAMES.get(place_type, [f"{place_type.replace('_', ' ').title()} Spot"])
    lat0, lon0 = CITY_COORDS.get(city, CITY_COORDS[DEFAULT_CITY])
    rng = random.Random(f"{place_type}-{city}")
    return [
        {
            "name": name,
            "category": place_type,
            "rating": round(rng.uniform(3.8, 4.9), 1),
            "latitude": lat0 + rng.uniform(-0.03, 0.03),
            "longitude": lon0 + rng.uniform(-0.03, 0.03),
            "google_place_id": f"mock-{place_type}-{name.lower().replace(' ', '-')}",
        }
        for name in names
    ]


def _live_search(place_type, city):
    params = {
        "query": f"{place_type.replace('_', ' ')} in {city}",
        "key": GOOGLE_PLACES_API_KEY,
    }
    response = requests.get(TEXT_SEARCH_URL, params=params, timeout=10)
    response.raise_for_status()
    results = []
    for r in response.json().get("results", []):
        location = r.get("geometry", {}).get("location", {})
        results.append(
            {
                "name": r.get("name"),
                "category": place_type,
                "rating": r.get("rating"),
                "latitude": location.get("lat"),
                "longitude": location.get("lng"),
                "google_place_id": r.get("place_id"),
            }
        )
    return results


def search_places(place_types, city=DEFAULT_CITY):
    """Look up places for each Google Places type. Uses mock data when no API key is configured."""
    search_fn = _mock_search if USE_MOCK_DATA else _live_search
    places = []
    for place_type in place_types:
        places.extend(search_fn(place_type, city))
    return places
