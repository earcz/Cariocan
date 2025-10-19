import pandas as pd, requests

def off_search(q, lang_code="en", page_size=25):
    try:
        url="https://world.openfoodfacts.org/cgi/search.pl"
        params={"search_terms":q,"search_simple":1,"action":"process","json":1,"page_size":page_size,"cc":"world"}
        r=requests.get(url,params=params,timeout=10); r.raise_for_status(); data=r.json()
        out=[]
        for p in data.get("products",[]):
            n=p.get("nutriments",{}) or {}
            fields=["energy-kcal_100g","proteins_100g","carbohydrates_100g","fat_100g","sugars_100g","fiber_100g","sodium_100g","salt_100g"]
            if any(k in n for k in fields):
                out.append({
                    "source":"OFF",
                    "name": p.get(f"product_name_{lang_code}") or p.get("product_name") or p.get(f"generic_name_{lang_code}") or p.get("generic_name") or "Unnamed",
                    "brand": p.get("brands",""),
                    "kcal_100g": n.get("energy-kcal_100g"),
                    "protein_100g": n.get("proteins_100g"),
                    "carbs_100g": n.get("carbohydrates_100g"),
                    "fat_100g": n.get("fat_100g"),
                    "sugars_100g": n.get("sugars_100g"),
                    "fiber_100g": n.get("fiber_100g"),
                    "sodium_100g": n.get("sodium_100g"),
                    "salt_100g": n.get("salt_100g")
                })
        return pd.DataFrame(out)
    except Exception:
        return pd.DataFrame()

def fdc_search(q, api_key, page_size=25):
    try:
        url="https://api.nal.usda.gov/fdc/v1/foods/search"
        params={"query":q,"pageSize":page_size,"api_key":api_key}
        r=requests.get(url,params=params,timeout=10); r.raise_for_status(); data=r.json()
        out=[]
        for item in data.get("foods",[]):
            n={x["nutrientName"]:x["value"] for x in item.get("foodNutrients",[]) if "value" in x}
            out.append({
                "source":"FDC",
                "name": item.get("description","Unnamed"),
                "brand": item.get("brandOwner",""),
                "kcal_100g": n.get("Energy","") or n.get("Energy (Atwater General Factors)",""),
                "protein_100g": n.get("Protein",""),
                "carbs_100g": n.get("Carbohydrate, by difference",""),
                "fat_100g": n.get("Total lipid (fat)",""),
                "sugars_100g": n.get("Sugars, total including NLEA",""),
                "fiber_100g": n.get("Fiber, total dietary",""),
                "sodium_100g": n.get("Sodium, Na",""),
                "salt_100g": ""
            })
        return pd.DataFrame(out)
    except Exception:
        return pd.DataFrame()

def macros_from_grams(row, grams):
    factor=grams/100.0
    vals = {}
    for k in ["kcal","protein","carbs","fat","sugars","fiber","sodium","salt"]:
        v=row.get(f"{k}_100g"); vals[k]= (float(v)*factor if isinstance(v,(int,float,str)) and str(v) not in ("","None","nan") else 0.0)
    return vals
