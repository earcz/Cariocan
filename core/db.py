import sqlite3

DB_NAME = "carioca_v27.db"

def get_conn():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        pw_hash BLOB NOT NULL,
        full_name TEXT,
        lang TEXT DEFAULT 'en',
        theme TEXT DEFAULT 'tropical',
        avatar TEXT,
        email TEXT,
        fdc_key TEXT,
        plan_type TEXT,
        meal_structure TEXT,
        age INT, sex TEXT, height_cm REAL, weight_kg REAL, bodyfat REAL,
        waist_cm REAL,
        birthdate TEXT,
        activity TEXT, target_weight REAL, training_days INT, fasting TEXT,
        created_at TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS weights(
        username TEXT, dt TEXT, weight REAL, waist REAL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS food_logs(
        username TEXT, dt TEXT, meal TEXT, food_name TEXT, grams REAL,
        kcal REAL, protein REAL, carbs REAL, fat REAL, sugars REAL, fiber REAL, sodium REAL, salt REAL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS workout_logs(
        username TEXT, dt TEXT, day TEXT, exercise TEXT, target_sets INT, target_reps INT,
        perf_sets INT, perf_reps INT, calories REAL
    )""")
    conn.commit()
    return conn
