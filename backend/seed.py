import pandas as pd
from sqlmodel import Session
from database import engine, create_db_and_tables
from models import User, Dish
from pathlib import Path

def seed():
    print("🏗️ Создание таблиц...")
    create_db_and_tables()
    
    # Пути к данным (на уровень выше backend)
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / "data"
    
    # 1. Загрузка пользователей
    profiles_path = data_dir / "profiles.csv"
    if profiles_path.exists():
        df_users = pd.read_csv(profiles_path)
        with Session(engine) as session:
            count = 0
            for _, row in df_users.iterrows():
                # Проверка на дубликаты
                existing = session.query(User).where(User.username == str(row['emp_id'])).first()
                if not existing:
                    user = User(
                        username=str(row['emp_id']),
                        password_hash="123456", # Пароль по умолчанию для MVP
                        full_name=f"Сотрудник {row['emp_id']}",
                        position=row['job_code'],
                        plant="Завод №1",
                        age=int(row['age']),
                        gender=row['gender'],
                        height_cm=float(row['height_cm']),
                        weight_kg=float(row['weight_kg']),
                        job_code=row['job_code'],
                        hard_exclusions=row['hard_exclusions'],
                        soft_dislikes=row['soft_dislikes'],
                        preferences=row['preferences'],
                        kcal_per_shift=int(row['kcal_per_shift']),
                        bmr=float(row['bmr']),
                        meal_target_kcal=float(row['meal_target_kcal'])
                    )
                    session.add(user)
                    count += 1
            session.commit()
            print(f"✅ Загружено {count} пользователей.")
            
    # 2. Загрузка блюд
    components_path = data_dir / "components.csv"
    if components_path.exists():
        df_dishes = pd.read_csv(components_path)
        with Session(engine) as session:
            count = 0
            for _, row in df_dishes.iterrows():
                existing = session.query(Dish).where(Dish.name == row['name']).first()
                if not existing:
                    dish = Dish(
                        name=row['name'],
                        category=row['category'],
                        calories=int(row['calories']),
                        protein=float(row['protein']),
                        carbs=float(row['carbs']),
                        fat=float(row['fat']),
                        tags=row['tags']
                    )
                    session.add(dish)
                    count += 1
            session.commit()
            print(f"✅ Загружено {count} блюд.")

if __name__ == "__main__":
    seed()