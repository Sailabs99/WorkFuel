from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

# --- Блюдо ---
class Dish(BaseModel):
    dish_id: int
    name: str
    category: str                    # "первое", "второе", "салат", "напиток" и т.д.
    calories: int
    proteins: float
    fats: float
    carbs: float
    allergens: List[str] = []        # ["глютен", "лактоза"]

# --- Данные одного дня ---
class DayMenu(BaseModel):
    date: date                       # 2026-05-10
    weekday: str                     # "Понедельник", "Вторник" ...
    is_weekend: bool = False
    dishes: List[Dish] = []
    summary: str = ""                # текст для кнопки "Подробнее"

# --- Недельное меню ---
class WeeklyMenu(BaseModel):
    days: List[DayMenu]              # ровно 7 элементов (Пн...Вс)
    last_updated: date               # дата, когда меню было загружено с сервера

# --- Профиль сотрудника ---
class EmployeeProfile(BaseModel):
    employee_id: int
    full_name: str                   # ФИО
    position: str                    # должность
    plant: str                       # завод / подразделение

# --- Запрос авторизации ---
class AuthRequest(BaseModel):
    username: str
    password: str

# --- Ответ авторизации ---
class AuthResponse(BaseModel):
    token: str                       # JWT
    profile: EmployeeProfile


from pydantic import BaseModel
