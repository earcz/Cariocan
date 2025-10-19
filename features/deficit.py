import streamlit as st
from core.calc import mifflin_st_jeor, activity_factor

def render(user_row):
    *_, age, sex, height_cm, weight_kg, bodyfat, birthdate, activity, target_weight, training_days, fasting, full_name, waist_cm = user_row
    bmr = mifflin_st_jeor(sex, weight_kg, height_cm, age)
    day_type = st.selectbox("Day Type", ["Workout Day","Rest Day"])
    deficit = st.slider("Deficit (%)", 5, 35, 25, step=1)
    base_tdee = bmr*activity_factor(activity) if day_type=="Workout Day" else bmr*1.35
    target_cal = round(base_tdee*(1-deficit/100))
    weekly_loss = round(((base_tdee-target_cal)*7)/7700,2)
    weight_3m = round((weight_kg or 80) - weekly_loss*12, 1)
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("TDEE", int(base_tdee)); c2.metric("Target Cal", int(target_cal)); c3.metric("Weekly Δ", f"{weekly_loss} kg"); c4.metric("3-Month Est.", f"{weight_3m} kg")
