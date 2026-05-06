from sqlmodel import SQLModel, create_engine, Session
import os

# Создаем файл БД в текущей директории backend
DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session