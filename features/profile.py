import streamlit as st
from datetime import date
from core.calc import mifflin_st_jeor, activity_factor, macro_split

def _t(key: str):
    lang = st.session_state.get("lang","en")
    tr = {
        "Full Name": "Ad Soyad",
        "Birthdate": "Doğum Tarihi",
        "Age": "Yaş",
        "Sex": "Cinsiyet",
        "Height (cm)": "Boy (cm)",
        "Weight (kg)": "Kilo (kg)",
        "Waist (cm)": "Bel (cm)",
        "Bodyfat (%)": "Yağ (%)",
        "Target Weight (kg)": "Hedef Kilo (kg)",
        "Avatar": "Profil Fotoğrafı",
        "Upload Photo": "Fotoğraf Yükle",
        "Activity Level": "Aktivite Seviyesi",
        "Training Days / Week": "Haftalık Antrenman (gün)",
        "Fasting": "Aralıklı Oruç",
        "Training Plan": "Antrenman Planı",
        "Meal Structure": "Öğün Yapısı",
        "E-mail": "E-posta",
        "USDA FDC API Key (optional)": "USDA FDC API Anahtarı (opsiyonel)",
        "Save": "Kaydet",
        "Updated": "Güncellendi",
        "BMR": "BMR",
        "TDEE": "TDEE",
        "Workout Day": "Antrenman Günü",
        "Rest Day": "Dinlenme Günü",
    }
    return tr.get(key, key) if lang == "tr" else key

def render(conn, user_row):
    (
        u, lang, avatar, email, fdc_key, plan_type, meal_structure, age, sex, height_cm,
        weight_kg, bodyfat, birthdate, activity, target_weight, training_days, fasting,
        full_name, waist_cm
    ) = user_row

    c1,c2,c3 = st.columns(3)

    with c1:
        full_name = st.text_input(_t("Full Name"), value=full_name or "")
        bd_val = None
        if birthdate:
            try:
                y,m,d = map(int, str(birthdate).split("-")); bd_val = date(y,m,d)
            except: bd_val = None
        bd_input = st.date_input(_t("Birthdate"), value=bd_val, min_value=date(1950,1,1), max_value=date(2035,12,31))
        if bd_input:
            today = date.today()
            age_calc = today.year - bd_input.year - ((today.month, today.day) < (bd_input.month, bd_input.day))
            age = age_calc
        age = st.number_input(_t("Age"), min_value=10, max_value=100, value=int(age) if age else 30)
        sex = st.selectbox(_t("Sex"), ["male","female"], index=0 if (sex or "male")=="male" else 1)
        height_cm = st.number_input(_t("Height (cm)"), 120, 230, int(height_cm) if height_cm else 175)

    with c2:
        weight_kg = st.number_input(_t("Weight (kg)"), 30.0, 250.0, float(weight_kg) if weight_kg else 80.0, step=0.1)
        waist_cm = st.number_input(_t("Waist (cm)"), 40.0, 200.0, float(waist_cm) if waist_cm else 90.0, step=0.5)
        bodyfat_val = float(bodyfat) if bodyfat not in (None,"") else 0.0
        bodyfat_in = st.number_input(_t("Bodyfat (%)"), 0.0, 60.0, bodyfat_val, step=0.1)
        bodyfat = bodyfat_in if bodyfat_in > 0 else None
        target_weight = st.number_input(_t("Target Weight (kg)"), 30.0, 250.0, float(target_weight) if target_weight else 80.0, step=0.1)
        st.subheader(_t("Avatar"))
        photo = st.file_uploader(_t("Upload Photo"), type=["png","jpg","jpeg"])
        if photo:
            import base64
            b64 = base64.b64encode(photo.read()).decode("utf-8")
            avatar = f"data:image/{photo.type.split('/')[-1]};base64,{b64}"

    with c3:
        act_opts = [
            "Sedentary (Desk Work)",
            "Light (1 day/week)",
            "Moderate (2-3 days/week)",
            "High (4-5 days/week)",
            "Very High (6-7 days/week)"
        ]
        # mevcut değeri uygun etikete map etmeye çalış
        cur_act = activity or "Light (1 day/week)"
        # eski kısa etiket geldiyse en yakına çevir
        if cur_act in ["Sedentary","Light","Moderate","High","Very High"]:
            map_short = {
                "Sedentary":"Sedentary (Desk Work)",
                "Light":"Light (1 day/week)",
                "Moderate":"Moderate (2-3 days/week)",
                "High":"High (4-5 days/week)",
                "Very High":"Very High (6-7 days/week)"
            }
            cur_act = map_short[cur_act]
        if cur_act not in act_opts:
            cur_act = "Light (1 day/week)"
        activity = st.selectbox(_t("Activity Level"), act_opts, index=act_opts.index(cur_act))

        training_days = st.slider(_t("Training Days / Week"), 1, 7, int(training_days) if training_days else 5)

        fast_opts = ["12:12","14:10","16:8","18:6"]
        current_fast = fasting or "16:8"
        if current_fast not in fast_opts:
            current_fast = "16:8"
        fasting = st.selectbox(_t("Fasting"), fast_opts, index=fast_opts.index(current_fast))

        plan_opts = ["Full Body","Push/Pull/Leg","Upper/Lower","Cardio & Core"]
        cur_plan = plan_type or "Full Body"
        if cur_plan not in plan_opts:
            cur_plan = "Full Body"
        plan_type = st.selectbox(_t("Training Plan"), plan_opts, index=plan_opts.index(cur_plan))

        meal_opts = ["2 Meals + 1 Snack","3 Meals","4 Meals"]
        cur_meal = meal_structure or "2 Meals + 1 Snack"
        if cur_meal not in meal_opts:
            cur_meal = "2 Meals + 1 Snack"
        meal_structure = st.selectbox(_t("Meal Structure"), meal_opts, index=meal_opts.index(cur_meal))

        email = st.text_input(_t("E-mail"), value=email or "")
        fdc_key = st.text_input(_t("USDA FDC API Key (optional)"), value=fdc_key or "")

    if st.button(_t("Save"), type="primary"):
        conn.execute("""
            UPDATE users SET
              full_name=?,
              lang=?,
              avatar=?,
              email=?,
              fdc_key=?,
              plan_type=?,
              meal_structure=?,
              age=?,
              sex=?,
              height_cm=?,
              weight_kg=?,
              bodyfat=?,
              birthdate=?,
              activity=?,
              target_weight=?,
              training_days=?,
              fasting=?,
              waist_cm=?
            WHERE username=?
        """, (
            full_name,
            st.session_state.get("lang","en"),
            avatar,
            email,
            fdc_key,
            plan_type,
            meal_structure,
            age,
            sex,
            height_cm,
            weight_kg,
            bodyfat,
            (bd_input.isoformat() if bd_input else None),
            activity,
            target_weight,
            training_days,
            fasting,
            waist_cm,
            u
        ))
        conn.commit()
        st.success(_t("Updated"))

    bmr = mifflin_st_jeor(sex, weight_kg, height_cm, age)
    tdee = bmr * activity_factor(activity)
    wcal = round(tdee * 0.75)
    rcal = round((bmr * 1.35) * 0.75)
    pc_w, cc_w, fc_w = macro_split(wcal, workout=True, weight=weight_kg)
    pc_r, cc_r, fc_r = macro_split(rcal, workout=False, weight=weight_kg)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric(_t("BMR"), f"{int(bmr)} kcal")
    c2.metric(_t("TDEE"), f"{int(tdee)} kcal")
    c3.metric(_t("Workout Day"), f"{wcal} kcal")
    c4.metric(_t("Rest Day"), f"{rcal} kcal")
    st.caption(f"🏋️ P {pc_w}g / C {cc_w}g / F {fc_w}g · 🛌 P {pc_r}g / C {cc_r}g / F {fc_r}g")
