# Baseline place types for each mood, used whenever there's no companion-specific
# override below. Every mood has a default so no (mood, companion) combination
# ever comes back empty.
MOOD_DEFAULTS = {
    "Romantic + Calm": ["restaurant", "cafe", "art_gallery"],
    "Adventurous + High Energy": ["amusement_park", "tourist_attraction"],
    "Creative + Chill": ["art_gallery", "book_store", "cafe"],
    "Outdoorsy + Active": ["park", "tourist_attraction"],
    "Low Energy + Cozy": ["cafe", "book_store"],
    "Fun + Playful": ["bowling_alley", "movie_theater"],
    "Curious + Intellectual": ["museum", "art_gallery"],
    "Spontaneous + Any Mood": ["restaurant", "cafe", "museum", "park", "movie_theater"],
}

# Overrides for specific (mood, companion) pairs where the recommendation
# should differ from the mood's default.
MOOD_MAP = {
    ("Low Energy + Cozy", "Partner"): ["cafe", "restaurant"],
}

COMPANIONS = ["Anyone", "Family", "Friends", "Partner", "Solo"]


def get_place_types(mood, companion):
    if (mood, companion) in MOOD_MAP:
        return MOOD_MAP[(mood, companion)]
    return MOOD_DEFAULTS.get(mood, [])

if __name__ == "__main__":
    print(get_place_types("Low Energy + Cozy", "Solo"))