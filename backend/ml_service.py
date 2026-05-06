import joblib
import os
import json
from pathlib import Path

# Путь к модели: backend/../ml/recommender.pkl
MODEL_PATH = Path(__file__).parent.parent / "ml" / "recommender.pkl"

try:
    with open(MODEL_PATH, "rb") as f:
        artifact = joblib.load(f)
    model = artifact["model"]
    feature_names = artifact["feature_names"]
    print("✅ ML Model loaded successfully.")
except FileNotFoundError:
    raise FileNotFoundError(f"Модель не найдена по пути: {MODEL_PATH}. Убедитесь, что вы запустили train_model.py или скопировали recommender.pkl в папку ml/")

def calculate_features(user, dish):
    """
    Формирует вектор признаков точно так же, как при обучении.
    """
    # 1. Базовые признаки
    features = {
        "weight_kg": user.weight_kg,
        "height_cm": user.height_cm,
        "age": user.age,
        "is_male": 1 if user.gender == "male" else 0,
        "kcal_per_shift": user.kcal_per_shift,
        "meal_target_kcal": user.meal_target_kcal,
        "calories": dish.calories,
        "protein": dish.protein,
        "carbs": dish.carbs,
        "fat": dish.fat,
    }
    
    # 2. Расчетные признаки
    target_per_meal = user.meal_target_kcal / 3
    cal_diff = abs(dish.calories - target_per_meal)
    features["cal_diff_ratio"] = cal_diff / target_per_meal if target_per_meal > 0 else 0
    
    # Macro score
    prot_ratio = dish.protein / dish.calories if dish.calories > 0 else 0
    if user.kcal_per_shift > 2500:
        features["macro_score"] = min(prot_ratio / 0.25, 1.0)
    else:
        features["macro_score"] = max(0, 1 - abs(prot_ratio - 0.15))
        
    # 3. Теги и предпочтения
    try:
        hard_exclusions = json.loads(user.hard_exclusions)
        soft_dislikes = json.loads(user.soft_dislikes)
        preferences = json.loads(user.preferences)
        dish_tags = json.loads(dish.tags)
    except:
        hard_exclusions = []
        soft_dislikes = []
        preferences = []
        dish_tags = []
    
    # Soft penalty
    soft_penalty = len(set(dish_tags) & set(soft_dislikes)) * 0.2
    features["soft_penalty"] = soft_penalty
    
    # Pref bonus
    pref_bonus = len(set(dish_tags) & set(preferences)) * 0.15
    features["pref_bonus"] = pref_bonus
    
    # 4. One-Hot Encoding для категорий и тегов
    # Мы проходимся по всем именам колонок, которые ожидает модель,
    # и заполняем их значениями. Если колонка есть в feature_names, но нет в features,
    # она получит значение 0 по умолчанию.
    
    # Категории
    categories = ["garnish", "protein", "side", "drink"]
    for cat in categories:
        col_name = f"cat_{cat}"
        features[col_name] = 1 if dish.category == cat else 0
        
    # Теги (все остальные колонки, которые не являются базовыми/расчетными/категориями)
    # Проще всего просто проверить, является ли имя колонки тегом из dish_tags
    known_keys = set(features.keys())
    for col in feature_names:
        if col not in known_keys:
            # Предполагаем, что это тег (например, 'caffeine', 'dairy' и т.д.)
            features[col] = 1 if col in dish_tags else 0
            
    # Собираем вектор в правильном порядке
    vector = [features.get(col, 0) for col in feature_names]
    return vector

def get_score(user, dish):
    try:
        vec = calculate_features(user, dish)
        score = model.predict([vec])[0]
        return max(0.0, min(1.0, score))
    except Exception as e:
        print(f"Ошибка предсказания: {e}")
        return 0.0