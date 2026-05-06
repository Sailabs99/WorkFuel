from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from datetime import date, timedelta
import json
from contextlib import asynccontextmanager
from passlib.context import CryptContext

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
        for day_idx in range(7):
            dishes_stmt = select(UserDailyDish).where(
                UserDailyDish.weekly_menu_id == saved_menu.id,
                UserDailyDish.day_index == day_idx
            )
            day_items = session.exec(dishes_stmt).all()
            
            dishes_list = []
            for item in day_items:
                d = item.dish
                # Исправлено: проверяем тип tags перед использованием
                if isinstance(d.tags, str):
                    allergens = json.loads(d.tags)
                elif isinstance(d.tags, list):
                    allergens = d.tags
                else:
                    allergens = []
                    
                dishes_list.append(DishSchema(
                    dish_id=d.dish_id,
                    name=d.name,
                    category=d.category,
                    calories=d.calories,
                    proteins=d.proteins,
                    fats=d.fats,
                    carbs=d.carbs,
                    allergens=allergens
                ))
            
            weekly_days.append(DayMenu(
                date=start_of_week + timedelta(days=day_idx),
                weekday=weekdays_ru[day_idx],
                is_weekend=(day_idx >= 5),
                dishes=dishes_list,
                summary="Рекомендовано ИИ (из кэша)"
            ))
    else:
        all_dishes = session.exec(select(Dish)).all()
        
        scored_dishes = []
        for dish in all_dishes:
            score = get_score(user, dish)
            scored_dishes.append((dish, score))
        
        scored_dishes.sort(key=lambda x: x[1], reverse=True)

        new_weekly_menu = UserWeeklyMenu(employee_id=user.id, start_date=start_of_week)
        session.add(new_weekly_menu)
        session.flush()

        chunk_size = 5
        current_index = 0

        for day_idx in range(7):
            is_weekend = (day_idx >= 5)
            dishes_for_day = []

            if not is_weekend:
                chunk = scored_dishes[current_index : current_index + chunk_size]
                current_index += chunk_size
                
                for dish, score in chunk:
                    link = UserDailyDish(
                        weekly_menu_id=new_weekly_menu.id,
                        day_index=day_idx,
                        dish_id=dish.id,
                        relevance_score=score
                    )
                    session.add(link)
                    
                    # Исправлено: проверяем тип tags
                    if isinstance(dish.tags, str):
                        allergens = json.loads(dish.tags)
                    elif isinstance(dish.tags, list):
                        allergens = dish.tags
                    else:
                        allergens = []
                    
                    dishes_for_day.append(DishSchema(
                        dish_id=dish.dish_id,
                        name=dish.name,
                        category=dish.category,
                        calories=dish.calories,
                        proteins=dish.proteins,
                        fats=dish.fats,
                        carbs=dish.carbs,
                        allergens=allergens
                    ))
            
            weekly_days.append(DayMenu(
                date=start_of_week + timedelta(days=day_idx),
                weekday=weekdays_ru[day_idx],
                is_weekend=is_weekend,
                dishes=dishes_for_day,
                summary="Сгенерировано ИИ и сохранено"
            ))
        
        session.commit()

    return WeeklyMenu(days=weekly_days, last_updated=today)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)