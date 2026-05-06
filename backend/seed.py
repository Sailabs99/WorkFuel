import pandas as pd
import json
import os
from pathlib import Path
from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models import Employee, Dish  # Убедитесь, что имена моделей совпадают
from passlib.context import CryptContext

# Настройка хеширования
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def parse_json_list(value):
    """Безопасный парсинг JSON-строки в список."""
    if pd.isna(value) or value == '':
        return []
    try:
        # Обработка случаев с двойными кавычками из CSV
        if isinstance(value, str):
            value = value.replace('""', '"')
        return json.loads(value) if isinstance(value, str) else value
    except (json.JSONDecodeError, TypeError):
        return []

def parse_tags(value):
    """Парсинг тегов из формата "['veg', 'gluten_free']" в список."""
    if pd.isna(value) or value == '':
        return []
    try:
        # Убираем квадратные скобки и кавычки, разбиваем по запятой
        if isinstance(value, str):
            cleaned = value.strip("[]'\"")
            if not cleaned:
                return []
            return [tag.strip().strip("'\"") for tag in cleaned.split(',')]
        return []
    except Exception:
        return []

def seed_data():
    print("🏗️ Создание таблиц БД...")
    create_db_and_tables()
    
    print("📂 Поиск папки с данными...")
    
    # Определяем путь к папке data
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    
    components_path = DATA_DIR / "components.csv"
    profiles_path = DATA_DIR / "profiles.csv"

    if not components_path.exists() or not profiles_path.exists():
        raise FileNotFoundError(f"❌ Не найдены CSV файлы в папке: {DATA_DIR}")

    with Session(engine) as session:
        # 1. Загрузка блюд
        print(f"📖 Чтение {components_path.name}...")
        df_dishes = pd.read_csv(components_path)
        
        dishes_added = 0
        for _, row in df_dishes.iterrows():
            # Проверяем наличие блюда по ID
            statement = select(Dish).where(Dish.dish_id == int(row['id']))
            existing = session.exec(statement).first()
            
            if not existing:
                dish = Dish(
                    dish_id=int(row['id']),
                    name=str(row['name']),
                    category=str(row['category']),
                    calories=int(row['calories']),
                    proteins=float(row['protein']),   # CSV: 'protein' → модель: 'proteins'
                    fats=float(row['fat']),            # CSV: 'fat' → модель: 'fats'
                    carbs=float(row['carbs']),
                    tags=parse_tags(row.get('tags', ''))  # Парсим теги как аллергены
                )  
                session.add(dish)
                dishes_added += 1
                
        session.commit()
        print(f"✅ Загружено {dishes_added} новых блюд (всего в файле: {len(df_dishes)}).")

        # 2. Загрузка сотрудников
        print(f"📖 Чтение {profiles_path.name}...")
        df_profiles = pd.read_csv(profiles_path)
        
        employees_added = 0
        for _, row in df_profiles.iterrows():
            emp_id = str(row['emp_id']).strip()
            
            statement = select(Employee).where(Employee.username == emp_id)
            existing = session.exec(statement).first()
            
            if not existing:
                employee = Employee(
                    username=emp_id,
                    password_hash=pwd_context.hash("123456"),  # Пароль по умолчанию
                    full_name=f"Сотрудник {emp_id}",
                    position=str(row['job_code']),
                    plant="Завод №1",
                    age=int(row['age']),
                    gender=str(row['gender']),
                    height_cm=float(row['height_cm']),
                    weight_kg=float(row['weight_kg']),
                    job_code=str(row['job_code']),
                    kcal_per_shift=int(row['kcal_per_shift']),
                    bmr=float(row['bmr']),
                    meal_target_kcal=float(row['meal_target_kcal']),
                    # Парсим JSON-строки в списки
                    hard_exclusions=parse_json_list(row['hard_exclusions']),
                    soft_dislikes=parse_json_list(row['soft_dislikes']),
                    preferences=parse_json_list(row['preferences'])
                )
                session.add(employee)
                employees_added += 1
                
        session.commit()
        print(f"✅ Загружено {employees_added} новых сотрудников (всего в файле: {len(df_profiles)}).")

    print("🎉 База данных успешно наполнена!")
    print("🔑 Логин для входа: EMP_001, Пароль: 123456")

if __name__ == "__main__":
    seed_data()