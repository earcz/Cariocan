def mifflin_st_jeor(sex:str, weight, height_cm, age):
    age = age or 30
    height_cm = height_cm or 175
    weight = weight or 80.0
    if sex == "male":
        return 10*weight + 6.25*height_cm - 5*age + 5
    else:
        return 10*weight + 6.25*height_cm - 5*age - 161

def activity_factor(level:str):
    return {"Sedentary":1.2,"Light":1.35,"Moderate":1.55,"High":1.75,"Very High":1.95}.get(level or "Light", 1.35)

def macro_split(cal, workout=True, weight=80):
    weight = weight or 80
    protein_g = round(2.0 * float(weight))
    carbs_g = round((1.8 if workout else 0.8) * float(weight))
    fat_g = max(0, round((cal - (protein_g*4 + carbs_g*4))/9))
    return protein_g, carbs_g, fat_g
