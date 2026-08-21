import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_name = os.path.join(BASE_DIR, "moodmap.db")

def get_connection():
    conn = sqlite3.connect(DB_name)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    schema_path = os.path.join(BASE_DIR,'sql', 'schema.sql')

    with open(schema_path, 'r', encoding='utf-8') as f:
        sql_script = f.read()

    cursor.executescript(sql_script)

    conn.commit()
    conn.close()

def ensure_schema():
    """Adds columns introduced after the initial schema, for databases created before them."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(visits)")
    columns = {row[1] for row in cursor.fetchall()}
    if "photo_path" not in columns:
        cursor.execute("ALTER TABLE visits ADD COLUMN photo_path TEXT")
    conn.commit()
    conn.close()

def seed_users():
    conn = get_connection()
    cursor = conn.cursor()

    users = [
        ("Shree", 'Edmonton'),
        ('Aarav', 'Edmonton'),
        ('Mannat', 'Edmonton')
    ]

    cursor.executemany("""INSERT OR IGNORE INTO users (username, city) VALUES (?, ?)""", users)

    conn.commit()
    conn.close()

def check_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, username, city, created_at FROM users")
    rows = cursor.fetchall()
    print("Users in the database:")
    for row in rows:
        print(row)

    conn.close()

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, city FROM users")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reviews WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM visits WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def create_user(username, city):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (username, city) VALUES (?, ?)",
        (username, city),
    )
    conn.commit()
    cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
    user_id = cursor.fetchone()[0]
    conn.close()
    return user_id

def get_or_create_place(place):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT place_id FROM places WHERE google_place_id = ?",
        (place["google_place_id"],),
    )
    row = cursor.fetchone()

    if row:
        place_id = row[0]
    else:
        cursor.execute(
            """INSERT INTO places (name, category, latitude, longitude, google_place_id, avg_rating)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                place["name"],
                place["category"],
                place["latitude"],
                place["longitude"],
                place["google_place_id"],
                place.get("rating"),
            ),
        )
        place_id = cursor.lastrowid

    conn.commit()
    conn.close()
    return place_id

def log_visit(user_id, place_id, mood, companion_type, photo_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO visits (user_id, place_id, mood_at_visit, companion_type, photo_path)
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, place_id, mood, companion_type, photo_path),
    )
    conn.commit()
    conn.close()

def get_user_history(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT p.name, p.category, v.mood_at_visit, v.companion_type, v.visited_at, v.photo_path
           FROM visits v
           JOIN places p ON v.place_id = p.place_id
           WHERE v.user_id = ?
           ORDER BY v.visited_at DESC""",
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    create_tables()
    seed_users()
    check_users()
    print("Database setup complete.")