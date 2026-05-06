from fastapi import APIRouter, Depends, Header, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import User, Dish
from schemas import WeeklyMenu, DayMenu, Dish as DishSchema
from ml_service import get_score
from jose import jwt, JWTError
from datetime import date, timedelta
import json

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

router = APIRouter()

def get_current_user(token: str = Header(...), session: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
        
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.get("/menu/weekly", response_model=WeeklyMenu)
def get_weekly_menu(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    # Получаем все блюда
    dishes = session.exec(select(Dish)).all()
    
    # Оцениваем каждое блюдо для текущего пользователя
    scored_dishes = []
    for dish in dishes:
        score = get_score(current_user, dish)
        scored_dishes.append((dish, score))
    
    # Сортируем по убыванию релевантности
    scored_dishes.sort(key=lambda x: x[1], reverse=True)
    
    # Берем топ-5 лучших блюд для демонстрации
    top_dishes = [d[0] for d in scored_dishes[:5]]
    
    # Генерируем меню на неделю
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    weekdays = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    
    days_menu = []
    
    for i in range(7):
        day_date = start_of_week + timedelta(days=i)
        is_weekend = i >= 5
        
        day_dishes_list = []
        if not is_weekend:
            # В будни показываем топ блюд
            for d in top_dishes:
                # Парсим теги в аллергены для фронтенда
                try:
                    allergens = json.loads(d.tags)
                except:
                    allergens = []
                    
                dish_schema = DishSchema(
                    dish_id=d.id,
                    name=d.name,
                    category=d.category,
                    calories=d.calories,
                    proteins=d.protein,
                    fats=d.fat,
                    carbs=d.carbs,
                    allergens=allergens
                )
                day_dishes_list.append(dish_schema)
        
        days_menu.append(DayMenu(
            date=day_date,
            weekday=weekdays[i],
            is_weekend=is_weekend,
            dishes=day_dishes_list,
            summary="Персональная рекомендация ИИ"
        ))
        
    return WeeklyMenu(days=days_menu, last_updated=today)