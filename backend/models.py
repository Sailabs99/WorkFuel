from sqlmodel import SQLModel, Field
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True) # Например, EMP_001
    password_hash: str
    full_name: str
    position: str
    plant: str
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    job_code: str
    hard_exclusions: str  # JSON строка
    soft_dislikes: str    # JSON строка
    preferences: str      # JSON строка
    kcal_per_shift: int
    bmr: float
    meal_target_kcal: float

class Dish(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category: str
    calories: int
    protein: float
    carbs: float
    fat: float
    tags: str # JSON строка, например ["veg", "gluten_free"]