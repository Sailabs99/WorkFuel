# models.py - исправленная версия
from sqlmodel import SQLModel, Field, Relationship, Column
from typing import List, Optional
from datetime import date
from sqlalchemy import JSON

class Employee(SQLModel, table=True):  # ← переименовали User → Employee
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str
    full_name: str
    position: str
    plant: str
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    job_code: str
    hard_exclusions: List[str] = Field(default_factory=list, sa_column=Column(JSON))  # ← исправлено
    soft_dislikes: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    preferences: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    kcal_per_shift: int
    bmr: float
    meal_target_kcal: float
    
    weekly_menus: List["UserWeeklyMenu"] = Relationship(back_populates="employee")

class Dish(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    dish_id: int = Field(unique=True, index=True)  # ← добавили dish_id из CSV
    name: str
    category: str
    calories: int
    proteins: float
    fats: float
    carbs: float
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))  # ← исправлено
    
    recommendations: List["UserDailyDish"] = Relationship(back_populates="dish")

class UserWeeklyMenu(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="employee.id")  # ← employee_id вместо user_id
    start_date: date
    employee: Employee = Relationship(back_populates="weekly_menus")
    daily_dishes: List["UserDailyDish"] = Relationship(back_populates="weekly_menu")

class UserDailyDish(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    weekly_menu_id: int = Field(foreign_key="userweeklymenu.id")
    day_index: int
    dish_id: int = Field(foreign_key="dish.id")
    relevance_score: float
    weekly_menu: UserWeeklyMenu = Relationship(back_populates="daily_dishes")
    dish: Dish = Relationship(back_populates="recommendations")