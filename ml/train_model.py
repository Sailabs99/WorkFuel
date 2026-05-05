import os
import json
import pandas as pd
import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
ML_DIR = BASE_DIR / "ml"
ML_DIR.mkdir(exist_ok=True)

print("📥 Загрузка данных...")
X = pd.read_csv(DATA_DIR / "X_train.csv")
y = pd.read_csv(DATA_DIR / "y_train.csv")["relevance_score"]

print("🔀 Разделение на train/test...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("🤖 Обучение RandomForestRegressor...")
model = RandomForestRegressor(
    n_estimators=100,
    max_depth=12,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# Оценка
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"📊 MAE: {mae:.3f} | R²: {r2:.3f}")

# Сохранение модели + метаданных
artifact = {
    "model": model,
    "feature_names": list(X.columns),  # Порядок колонок критичен для инференса
    "target_mean": float(y.mean()),
    "target_std": float(y.std())
}
model_path = ML_DIR / "recommender.pkl"
joblib.dump(artifact, model_path)

print(f"💾 Артефакт сохранён: {model_path}")
print("✅ Готово к интеграции в FastAPI.")