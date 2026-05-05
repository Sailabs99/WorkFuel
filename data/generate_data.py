import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from faker import Faker

# Фиксируем воспроизводимость
np.random.seed(42)
Faker.seed(42)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

print("🔄 Генерация синтетических данных...")

# 1. Энергозатраты по сменам/должностям
shift_energy = pd.DataFrame({
    "job_code": ["operator_light", "operator_medium", "operator_heavy", "welder", "packer", "engineer_office"],
    "job_name": ["Оператор ЛК", "Оператор ЧПУ", "Слесарь", "Сварщик", "Упаковщик", "Инженер"],
    "kcal_per_shift": [1800, 2200, 3000, 3200, 1900, 1500]
})

# 2. Компоненты меню (раздельные элементы)
components = [
    {"name": "Гречка отварная", "category": "garnish", "calories": 130, "protein": 4.5, "carbs": 28, "fat": 2.0, "tags": ["veg", "gluten_free"]},
    {"name": "Рис белый", "category": "garnish", "calories": 130, "protein": 2.5, "carbs": 28, "fat": 0.5, "tags": ["veg", "gluten_free"]},
    {"name": "Макароны", "category": "garnish", "calories": 150, "protein": 5.0, "carbs": 30, "fat": 1.0, "tags": ["veg", "gluten"]},
    {"name": "Картофельное пюре", "category": "garnish", "calories": 110, "protein": 2.5, "carbs": 18, "fat": 3.0, "tags": ["veg", "dairy"]},
    {"name": "Овощи гриль", "category": "garnish", "calories": 70, "protein": 2.0, "carbs": 10, "fat": 3.0, "tags": ["veg", "low_cal"]},
    {"name": "Котлета куриная", "category": "protein", "calories": 220, "protein": 18.0, "carbs": 8.0, "fat": 12.0, "tags": ["poultry"]},
    {"name": "Куриная грудка", "category": "protein", "calories": 160, "protein": 30.0, "carbs": 0.0, "fat": 3.0, "tags": ["poultry", "diet"]},
    {"name": "Говядина тушеная", "category": "protein", "calories": 280, "protein": 25.0, "carbs": 2.0, "fat": 20.0, "tags": ["red_meat", "high_fat"]},
    {"name": "Сосиски", "category": "protein", "calories": 290, "protein": 12.0, "carbs": 3.0, "fat": 26.0, "tags": ["processed", "pork"]},
    {"name": "Рыба минтай", "category": "protein", "calories": 140, "protein": 22.0, "carbs": 0.0, "fat": 4.0, "tags": ["fish", "diet"]},
    {"name": "Печень говяжья", "category": "protein", "calories": 130, "protein": 20.0, "carbs": 3.0, "fat": 4.0, "tags": ["red_meat", "iron"]},
    {"name": "Салат капустный", "category": "side", "calories": 40, "protein": 1.0, "carbs": 5.0, "fat": 2.0, "tags": ["veg", "fiber"]},
    {"name": "Винегрет", "category": "side", "calories": 80, "protein": 1.5, "carbs": 9.0, "fat": 4.0, "tags": ["veg"]},
    {"name": "Компот ягодный", "category": "drink", "calories": 60, "protein": 0.2, "carbs": 15.0, "fat": 0.0, "tags": ["sweet", "fruit"]},
    {"name": "Чай черный", "category": "drink", "calories": 0, "protein": 0.0, "carbs": 0.0, "fat": 0.0, "tags": ["hot", "caffeine"]},
    {"name": "Кефир 2.5%", "category": "drink", "calories": 50, "protein": 3.0, "carbs": 4.0, "fat": 2.5, "tags": ["dairy", "probiotic"]},
]
df_comp = pd.DataFrame(components)
df_comp["id"] = range(1, len(df_comp) + 1)
df_comp["is_available_today"] = True

# 3. Профили сотрудников
tags_pool = ["gluten", "lactose", "fish", "pork", "spicy", "mushroom", "nuts"]
prefs_pool = ["diet", "high_protein", "veg", "low_carb", "hot", "fiber"]
jobs = shift_energy["job_code"].tolist()

profiles = []
for i in range(1, 201):
    age = int(np.random.uniform(20, 55))
    gender = np.random.choice(["male", "female"])
    height = np.random.uniform(155, 195) if gender == "male" else np.random.uniform(150, 175)
    weight = np.random.uniform(50, 120)
    job = np.random.choice(jobs)
    
    hard = list(np.random.choice(tags_pool, size=np.random.randint(0, 2), replace=False))
    soft = list(np.random.choice(tags_pool, size=np.random.randint(0, 3), replace=False))
    pref = list(np.random.choice(prefs_pool, size=np.random.randint(0, 3), replace=False))
    
    profiles.append({
        "emp_id": f"EMP_{i:03d}", "age": age, "gender": gender,
        "height_cm": round(height, 1), "weight_kg": round(weight, 1),
        "job_code": job,
        "hard_exclusions": json.dumps(hard),
        "soft_dislikes": json.dumps(soft),
        "preferences": json.dumps(pref)
    })
df_prof = pd.DataFrame(profiles)

# 4. Физиология и целевая калорийность
df_prof = df_prof.merge(shift_energy[["job_code", "kcal_per_shift"]], on="job_code", how="left")
df_prof["bmr"] = np.where(
    df_prof["gender"] == "male",
    10*df_prof["weight_kg"] + 6.25*df_prof["height_cm"] - 5*df_prof["age"] + 5,
    10*df_prof["weight_kg"] + 6.25*df_prof["height_cm"] - 5*df_prof["age"] - 161
)
df_prof["meal_target_kcal"] = (df_prof["bmr"] + df_prof["kcal_per_shift"]) * 0.35  # ~35% суточной нормы

# 5. Cross-Join для обучения
df_train = df_prof.merge(df_comp, how="cross")

# --- Feature Engineering ---
df_train["cal_diff_ratio"] = abs(df_train["calories"] - df_train["meal_target_kcal"]/3) / (df_train["meal_target_kcal"]/3)
df_train["hard_list"] = df_train["hard_exclusions"].apply(json.loads)
df_train["soft_list"] = df_train["soft_dislikes"].apply(json.loads)
df_train["pref_list"] = df_train["preferences"].apply(json.loads)

df_train["has_hard"] = df_train.apply(lambda r: any(t in r["tags"] for t in r["hard_list"]), axis=1)
df_train["soft_penalty"] = df_train.apply(lambda r: len(set(r["tags"]) & set(r["soft_list"])) * 0.2, axis=1)
df_train["pref_bonus"] = df_train.apply(lambda r: len(set(r["tags"]) & set(r["pref_list"])) * 0.15, axis=1)

def macro_score(row):
    prot_ratio = row["protein"] / row["calories"] if row["calories"] > 0 else 0
    if row["kcal_per_shift"] > 2500:
        return min(prot_ratio / 0.25, 1.0)
    return max(0, 1 - abs(prot_ratio - 0.15))
df_train["macro_score"] = df_train.apply(macro_score, axis=1)

# Целевая переменная
df_train["relevance_score"] = np.clip(
    0.45 * np.maximum(0, 1 - df_train["cal_diff_ratio"]) +
    0.25 * df_train["macro_score"] +
    0.20 * df_train["pref_bonus"] -
    0.10 * df_train["soft_penalty"] -
    np.where(df_train["has_hard"], 1.0, 0.0),
    0.0, 1.0
)

# 6. Подготовка X для ML
df_ml = df_train.copy()
df_ml["is_male"] = (df_ml["gender"] == "male").astype(int)
df_ml["category"] = pd.Categorical(df_ml["category"])
df_ml = pd.get_dummies(df_ml, columns=["category"], prefix="cat", drop_first=True)

df_ml["tags_str"] = df_ml["tags"].apply(lambda x: ",".join(x))
tags_dummies = df_ml["tags_str"].str.get_dummies(sep=",")
df_ml = pd.concat([df_ml, tags_dummies], axis=1)

base_feats = ["weight_kg", "height_cm", "age", "is_male", "kcal_per_shift", "meal_target_kcal",
              "calories", "protein", "carbs", "fat", "cal_diff_ratio", "soft_penalty", "pref_bonus", "macro_score"]
cat_feats = [c for c in df_ml.columns if c.startswith("cat_")]
tag_feats = list(tags_dummies.columns)
feature_cols = base_feats + cat_feats + tag_feats

X = df_ml[feature_cols].fillna(0)
y = df_ml["relevance_score"]

# Сохранение
shift_energy.to_csv(DATA_DIR / "shift_energy.csv", index=False)
df_comp.to_csv(DATA_DIR / "components.csv", index=False)
df_prof.to_csv(DATA_DIR / "profiles.csv", index=False)
X.to_csv(DATA_DIR / "X_train.csv", index=False)
y.to_csv(DATA_DIR / "y_train.csv", index=False)

print("✅ Генерация завершена!")
print(f"📁 Папка {DATA_DIR} содержит:")
for f in DATA_DIR.glob("*.csv"):
    print(f"  • {f.name} ({pd.read_csv(f).shape[0]} строк)")