MOOD_MAP = {
    ("Romantic + Calm", "Partner"): ["restaurant", "cafe", "art_gallery"],
    
    ("Adventurous + High Energy", "Friends"): ["amusement_park", "tourist_attraction"],
    ("Adventurous + High Energy", "Partner"): ["amusement_park", "tourist_attraction"],
    
    ("Creative + Chill", "Solo"): ["art_gallery", "book_store", "cafe"],
    ("Creative + Chill", "Friends"): ["art_gallery", "cafe"],
    
    ("Outdoorsy + Active", "Solo"): ["park"],
    ("Outdoorsy + Active", "Friends"): ["park", "tourist_attraction"],
    
    ("Low Energy + Cozy", "Solo"): ["cafe", "book_store"],
    ("Low Energy + Cozy", "Partner"): ["cafe", "restaurant"],
    
    ("Fun + Playful", "Friends"): ["bowling_alley", "movie_theater"],
    ("Fun + Playful", "Family"): ["bowling_alley", "movie_theater"],
    
    ("Curious + Intellectual", "Solo"): ["museum", "art_gallery"],
    ("Curious + Intellectual", "Partner"): ["museum", "art_gallery"],
    
    ("Spontaneous + Any Mood", "Anyone"): [
        "restaurant", "cafe", "museum", "park", "movie_theater"
    ]
}


def get_place_types(mood, companion):
    return MOOD_MAP.get((mood, companion), [])

if __name__ == "__main__":
    print(get_place_types("Low Energy + Cozy", "Solo"))