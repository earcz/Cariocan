def mifflin_st_jeor(sex: str, weight, height_cm, age):
    weight = float(weight or 70)
    height_cm = float(height_cm or 175)
    age = int(age or 30)
    if (sex or "male").lower() == "male":
        return 10*weight + 6.25*height_cm - 5*age + 5
    return 10*weight + 6.25*height_cm - 5*age - 161

def _normalize_activity(label: str) -> str:
    if not label:
        return "light"
    s = label.lower()
    # hem kısa hem açıklamalı etiketlerle eşleşir
    if s.startswith("sedentary"): return "sedentary"
    if s.startswith("light"):     return "light"
    if s.startswith("moderate"):  return "moderate"
    if s.startswith("high"):      return "high"
    if s.startswith("very high"): return "very_high"
    # Türkçe karşılıklar olursa
    if "masa" in s or "ofis" in s: return "sedentary"
    return "light"

def activity_factor(label: str) -> float:
    key = _normalize_activity(label)
    factors = {
        "sedentary": 1.2,
        "light": 1.35,
        "moderate": 1.55,
        "high": 1.75,
        "very_high": 1.95,
    }
    return factors.get(key, 1.35)

def macro_split(cal, workout=True, weight=80):
    weight = float(weight or 80)
    cal = float(cal or 0)
    protein_g = round(2.0 * weight)
    carbs_g = round((1.8 if workout else 0.8) * weight)
    fat_g = max(0, round((cal - (protein_g*4 + carbs_g*4))/9))
    return protein_g, carbs_g, fat_g
