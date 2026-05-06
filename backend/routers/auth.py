from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import Employee
from schemas import AuthRequest, AuthResponse, EmployeeProfile
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 1 неделя

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()

def create_access_token(data: dict):
    """Создает JWT токен с временем жизни"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/auth/login", response_model=AuthResponse)
def login(request: AuthRequest, session: Session = Depends(get_session)):
    # Ищем пользователя по username
    statement = select(Employee).where(Employee.username == request.username)
    user = session.exec(statement).first()
    
    # Проверяем существование пользователя
    if not user:
        raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    
    # Проверяем пароль - пробуем оба варианта для совместимости
    try:
        # Пробуем проверить как хешированный пароль
        if pwd_context.verify(request.password, user.password_hash):
            pass  # Пароль верный
        else:
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    except (ValueError, TypeError):
        # Если хеш невалидный, проверяем прямое совпадение (для старых данных)
        if request.password != user.password_hash:
            raise HTTPException(status_code=401, detail="Неверный логин или пароль")
    
    # Создаем токен
    token = create_access_token(data={"sub": user.username})
    
    # Формируем профиль для ответа
    profile = EmployeeProfile(
        employee_id=user.id,
        full_name=user.full_name,
        position=user.position,
        plant=user.plant
    )
    
    return AuthResponse(token=token, profile=profile)