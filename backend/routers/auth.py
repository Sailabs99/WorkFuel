from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database import get_session
from models import User
from schemas import AuthRequest, AuthResponse, EmployeeProfile
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "mysecretkey" # Для MVP можно захардкодить
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

router = APIRouter()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/auth/login", response_model=AuthResponse)
def login(request: AuthRequest, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == request.username)
    user = session.exec(statement).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Неверный логин")
        
    # Простая проверка пароля для MVP (в seed.py пароль "123456")
    if request.password != user.password_hash:
        raise HTTPException(status_code=401, detail="Неверный пароль")
    
    token = create_access_token(data={"sub": user.username})
    
    profile = EmployeeProfile(
        employee_id=user.id,
        full_name=user.full_name,
        position=user.position,
        plant=user.plant
    )
    
    return AuthResponse(token=token, profile=profile)