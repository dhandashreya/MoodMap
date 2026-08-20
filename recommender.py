from api_utils import search_places
from mood_logic import get_place_types


def recommend_places(mood, companion, city):
    place_types = get_place_types(mood, companion)
    if not place_types:
        return []
    places = search_places(place_types, city)
    places.sort(key=lambda p: p.get("rating") or 0, reverse=True)
    return places


if __name__ == "__main__":
    for place in recommend_places("Low Energy + Cozy", "Solo", "Edmonton"):
        print(place["name"], place["category"], place["rating"])
