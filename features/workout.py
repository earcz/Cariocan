import streamlit as st
from datetime import date

def render(conn, user_row):
    # --- 🧱 Tablo güvenliği: workout_logs var mı, kolonlar tam mı ---
    conn.execute("""
        CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            dt TEXT,
            day TEXT,
            exercise TEXT,
            target_sets INT,
            target_reps INT,
            perf_sets INT,
            perf_reps INT,
            calories REAL
        )
    """)
    # Eksik kolonları tamamla (eski DB'lerde sorun olmasın)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(workout_logs)")}
    required = {
        "username": "TEXT", "dt": "TEXT", "day": "TEXT",
        "exercise": "TEXT", "target_sets": "INT", "target_reps": "INT",
        "perf_sets": "INT", "perf_reps": "INT", "calories": "REAL"
    }
    for c, t in required.items():
        if c not in cols:
            try:
                conn.execute(f"ALTER TABLE workout_logs ADD COLUMN {c} {t}")
            except:
                pass
    conn.commit()

    # --- 🧍 Kullanıcı bilgisi ---
    user = st.session_state.get("user", user_row[0])
    plan_type = user_row[6]

    # --- Gün seçimi ---
    day = st.selectbox("Select Day", ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])

    # --- Egzersiz planları ---
    alts = {
        "Squat":["Leg Press","Goblet Squat","Hack Squat"],
        "Bench Press":["Incline DB Press","Push-up","Machine Chest Press"],
        "Barbell Row":["Seated Row","Lat Pulldown","Dumbbell Row"],
        "Romanian Deadlift":["Hip Thrust","Back Extension","Good Morning"],
        "Shoulder Press":["Arnold Press","Machine Shoulder Press","Push Press"],
        "Walking Lunge":["Reverse Lunge","Split Squat","Step-up"],
        "Deadlift":["Rack Pull","Trap Bar Deadlift","Sumo Deadlift"],
        "Lat Pulldown":["Pull-up","Seated Row","One-arm Pulldown"],
        "Leg Curl":["Romanian Deadlift","Glute Ham Raise","Nordic Curl"]
    }

    muscles = {
        "Quads":"https://i.imgur.com/7j3m3x1.png",
        "Hamstrings/Glutes":"https://i.imgur.com/9jJH4nR.png",
        "Chest":"https://i.imgur.com/7V5vZxj.png",
        "Back":"https://i.imgur.com/2UKo1e8.png",
        "Shoulders":"https://i.imgur.com/9y2tS6I.png",
        "Core":"https://i.imgur.com/YH8cXvE.png",
        "Arms":"https://i.imgur.com/2b3Rkq4.png",
        "Calves":"https://i.imgur.com/4iL3nq8.png"
    }

    # --- Plan yapısı ---
    if plan_type=="Push/Pull/Leg":
        schedule = {
            "Monday":[("Bench Press","4x8","Chest"),("Shoulder Press","3x12","Shoulders")],
            "Wednesday":[("Barbell Row","4x8","Back"),("Lat Pulldown","3x12","Back")],
            "Friday":[("Squat","4x8","Quads"),("Leg Curl","3x12","Hamstrings/Glutes")]
        }
    elif plan_type=="Upper/Lower":
        schedule = {
            "Monday":[("Bench Press","4x8","Chest"),("Barbell Row","4x8","Back"),("Shoulder Press","3x12","Shoulders")],
            "Tuesday":[("Squat","4x8","Quads"),("Romanian Deadlift","3x10","Hamstrings/Glutes")],
            "Thursday":[("Incline DB Press","3x10","Chest"),("Seated Row","3x12","Back")],
            "Friday":[("Leg Press","4x12","Quads"),("Leg Curl","3x12","Hamstrings/Glutes")]
        }
    elif plan_type=="Cardio & Core":
        schedule = {
            "Monday":[("Treadmill Incline","40min","Cardio"),("Plank","3x max","Core")],
            "Wednesday":[("Treadmill Incline","40min","Cardio"),("Leg Raise","3x15","Core")],
            "Friday":[("Treadmill Incline","40min","Cardio"),("Side Plank","3x30s/side","Core")]
        }
    else:
        schedule = {
            "Monday":[("Squat","4x8","Quads"),("Bench Press","4x8","Chest"),("Barbell Row","4x10","Back"),("Shoulder Press","3x12","Shoulders")],
            "Wednesday":[("Romanian Deadlift","3x10","Hamstrings/Glutes"),("Incline DB Press","3x12","Chest"),("Seated Row","3x12","Back"),("Walking Lunge","2x20","Quads")],
            "Friday":[("Deadlift","3x5","Back"),("Bench Press","4x6","Chest"),("Lat Pulldown","3x12","Back"),("Leg Curl","3x12","Hamstrings/Glutes")]
        }

    # --- Bugünün planı ---
    todays = schedule.get(day, [])
    total_burn = 0
    if not todays:
        st.info("Rest day 💤")
        return

    for i, (name, sr, mg) in enumerate(todays, start=1):
        cols = st.columns([3,2,2])
        with cols[0]:
            st.markdown(f"**{i}. {name}** — Target: {sr}")
            try:
                t_sets, t_reps = sr.lower().split("x")
                t_sets = int(t_sets.replace("~","").strip())
                t_reps = int(''.join([c for c in t_reps if c.isdigit()]))
            except:
                t_sets, t_reps = 3, 10
            perf_sets = st.number_input("Sets", 0, 20, t_sets, key=f"s_{i}")
            perf_reps = st.number_input("Reps", 0, 100, t_reps, key=f"r_{i}")
            cal = round(0.1 * perf_sets * perf_reps)
            st.write(f"≈ **{cal} kcal**")
            
            # ✅ Kayıt işlemi (hatasız INSERT)
            if st.button("Save", key=f"save_{i}"):
                try:
                    conn.execute("""
                        INSERT INTO workout_logs(username, dt, day, exercise, target_sets, target_reps, perf_sets, perf_reps, calories)
                        VALUES(?,?,?,?,?,?,?,?,?)
                    """, (
                        user, date.today().isoformat(), day, name, t_sets, t_reps,
                        int(perf_sets), int(perf_reps), cal
                    ))
                    conn.commit()
                    st.success(f"{name} saved (+{cal} kcal)")
                except Exception as e:
                    st.error(f"Insert error: {e}")
            total_burn += cal

        with cols[1]:
            img = muscles.get(mg)
            if img:
                st.image(img, caption=mg, width=140)
        with cols[2]:
            st.markdown(f"[Video Guide]({'https://www.youtube.com/results?search_query=' + name.replace(' ','+')})")

    st.info(f"**Total Burn (est): {int(total_burn)} kcal**")
