from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from datetime import date, timedelta
import json
from contextlib import asynccontextmanager
from passlib.context import CryptContext
from collections import defaultdict
from database import engine, create_db_and_tables, get_session
from models import Employee, Dish, UserWeeklyMenu, UserDailyDish
from schemas import WeeklyMenu, DayMenu, Dish as DishSchema, AuthRequest, AuthResponse, EmployeeProfile
from ml_service import get_score
from jose import jwt, JWTError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Запуск приложения...")
    create_db_and_tables()
    print("✅ База данных готова")
    yield
    print("👋 Завершение работы приложения...")

app = FastAPI(title="Diet Recommender API", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Авторизация ---
@app.post("/auth/login", response_model=AuthResponse)
def login(request: AuthRequest, session: Session = Depends(get_session)):
    statement = select(Employee).where(Employee.username == request.username)
    user = session.exec(statement).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    
    password_ok = False
    try:
        password_ok = pwd_context.verify(request.password, user.password_hash)
    except (ValueError, TypeError):
        password_ok = (request.password == user.password_hash)
    
    if not password_ok:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    
    token = jwt.encode({"sub": user.username}, "secret-key", algorithm="HS256")
    
    return AuthResponse(
        token=token,
        profile=EmployeeProfile(
            employee_id=user.id,
            full_name=user.full_name,
            position=user.position,
            plant=user.plant
        )
    )


def generate_smart_summary(dishes_list, user):
    """
    Считает сумму КБЖУ и генерирует объяснение выбора.
    """
    if not dishes_list:
        return "Выходной день"

    total_cal = sum(d.calories for d in dishes_list)
    total_prot = sum(d.proteins for d in dishes_list)
    total_fat = sum(d.fats for d in dishes_list)
    total_carb = sum(d.carbs for d in dishes_list)

    # Формируем строку с цифрами
    stats = f"Ккал: {total_cal} | Б: {total_prot:.1f}г | Ж: {total_fat:.1f}г | У: {total_carb:.1f}г"
    
    # Логика "Почему выбрано"
    reasons = []
    
    # 1. Проверка калорийности (сравниваем с целью сотрудника)
    target = user.meal_target_kcal if user.meal_target_kcal else 800
    if 0.9 * target <= total_cal <= 1.1 * target:
        reasons.append("Оптимально по калориям")
    elif total_cal < 600:
        reasons.append("Легкий прием пищи")
    else:
        reasons.append("Сытный обед")

    # 2. Проверка белка (важно для заводов)
    if user.kcal_per_shift and user.kcal_per_shift > 2500 and total_prot > 25:
        reasons.append("Высокий белок для тяжелой смены")
    elif total_prot > 20:
        reasons.append("Достаточный белок")

    # 3. Проверка баланса жиров (вредно > 40г за раз)
    if total_fat > 40:
        reasons.append("Повышенная жирность")
    
    reason_text = " | ".join(reasons) if reasons else "Сбалансированный рацион"
    
    return f"{stats} | {reason_text}"


# --- Меню ---
@app.get("/menu/weekly", response_model=WeeklyMenu)
def get_weekly_menu(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, "secret-key", algorithms=["HS256"])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = session.exec(select(Employee).where(Employee.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    weekdays_ru = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

    existing_menu_stmt = select(UserWeeklyMenu).where(
        UserWeeklyMenu.employee_id == user.id,
        UserWeeklyMenu.start_date == start_of_week
    )
    saved_menu = session.exec(existing_menu_stmt).first()

    weekly_days = []

    if saved_menu:
        # Если меню уже есть в кэше
        for day_idx in range(7):
            dishes_stmt = select(UserDailyDish).where(
                UserDailyDish.weekly_menu_id == saved_menu.id,
                UserDailyDish.day_index == day_idx
            )
            day_items = session.exec(dishes_stmt).all()
            
            dishes_list = []
            for item in day_items:
                d = item.dish
                # Парсинг тегов
                allergens = d.tags if isinstance(d.tags, list) else json.loads(d.tags) if d.tags else []
                
                dishes_list.append(DishSchema(
                    dish_id=d.dish_id, name=d.name, category=d.category,
                    calories=d.calories, proteins=d.proteins, fats=d.fats, carbs=d.carbs,
                    allergens=allergens
                ))
            
            # 🔴 ВЫЗЫВАЕМ НАШУ НОВУЮ ФУНКЦИЮ ЗДЕСЬ
            summary_text = generate_smart_summary(dishes_list, user)
            
            weekly_days.append(DayMenu(
                date=start_of_week + timedelta(days=day_idx),
                weekday=weekdays_ru[day_idx],
                is_weekend=(day_idx >= 5),
                dishes=dishes_list,
                summary=summary_text 
            ))
    else:
        all_dishes = session.exec(select(Dish)).all()
        
        scored_dishes = []
        for dish in all_dishes:
            score = get_score(user, dish)
            scored_dishes.append((dish, score))
        
        scored_dishes.sort(key=lambda x: x[1], reverse=True)

        # Группируем по категориям
        by_category = {"garnish": [], "protein": [], "side": [], "drink": []}
        for dish, score in scored_dishes:
            if dish.category in by_category:
                by_category[dish.category].append((dish, score))

        # Сортируем каждую категорию
        for cat in by_category:
            by_category[cat].sort(key=lambda x: x[1], reverse=True)

        new_weekly_menu = UserWeeklyMenu(employee_id=user.id, start_date=start_of_week)
        session.add(new_weekly_menu)
        session.flush()

        required_cats = ["garnish", "protein", "side", "drink"]

        for day_idx in range(7):
            is_weekend = day_idx >= 5
            dishes_for_day = []

            if not is_weekend:
                for cat in required_cats:
                    cat_list = by_category.get(cat, [])
                    if not cat_list:
                        continue
                    
                    # ЧЕРЕДУЕМ блюда по дням: день 0 -> блюдо 0, день 1 -> блюдо 1, и т.д.
                    # Если блюд меньше чем дней, используем modulo для повторения
                    selected_idx = day_idx % len(cat_list)
                    selected_dish, selected_score = cat_list[selected_idx]
                    
                    link = UserDailyDish(
                        weekly_menu_id=new_weekly_menu.id,
                        day_index=day_idx,
                        dish_id=selected_dish.id,
                        relevance_score=selected_score
                    )
                    session.add(link)
                    
                    if isinstance(selected_dish.tags, str):
                        allergens = json.loads(selected_dish.tags)
                    elif isinstance(selected_dish.tags, list):
                        allergens = selected_dish.tags
                    else:
                        allergens = []
                    
                    dishes_for_day.append(DishSchema(
                        dish_id=selected_dish.dish_id,
                        name=selected_dish.name,
                        category=selected_dish.category,
                        calories=selected_dish.calories,
                        proteins=selected_dish.proteins,
                        fats=selected_dish.fats,
                        carbs=selected_dish.carbs,
                        allergens=allergens
                    ))
                
                # Генерируем summary с КБЖУ
                summary_text = generate_smart_summary(dishes_for_day, user)
            else:
                summary_text = "Выходной день"

            weekly_days.append(DayMenu(
                date=start_of_week + timedelta(days=day_idx),
                weekday=weekdays_ru[day_idx],
                is_weekend=is_weekend,
                dishes=dishes_for_day,
                summary=summary_text
            ))
        
        session.commit()

    return WeeklyMenu(days=weekly_days, last_updated=today)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)