from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_db_and_tables
from routers import auth, menu

app = FastAPI(title="Diet Recommender API")

# Разрешаем запросы от Kivy приложения
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(auth.router)
app.include_router(menu.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)