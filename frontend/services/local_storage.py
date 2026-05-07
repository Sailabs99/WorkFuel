"""
Локальное хранилище для кэширования данных между сессиями.
"""

import json
import os
from datetime import date
from shared_models.schemas import EmployeeProfile, WeeklyMenu

# Пути к файлам относительно папки приложения (обычно ~/.kivy/app_name)
# Но для простоты будем хранить в папке frontend/user_data
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'user_data')
os.makedirs(BASE_DIR, exist_ok=True)

TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')
PROFILE_FILE = os.path.join(BASE_DIR, 'profile.json')
MENU_FILE = os.path.join(BASE_DIR, 'menu.json')
AVATAR_FILE = os.path.join(BASE_DIR, 'avatar.png')


def save_token(token: str):
    with open(TOKEN_FILE, 'w', encoding='utf-8') as f:
        json.dump({'token': token, 'saved_at': str(date.today())}, f)


def load_token() -> str | None:
    if not os.path.exists(TOKEN_FILE):
        return None
    try:
        with open(TOKEN_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('token')
    except:
        return None


def delete_token():
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)


def save_profile(profile: EmployeeProfile):
    with open(PROFILE_FILE, 'w', encoding='utf-8') as f:
        json.dump(profile.model_dump(), f, ensure_ascii=False, indent=2)


def load_profile() -> EmployeeProfile | None:
    if not os.path.exists(PROFILE_FILE):
        return None
    try:
        with open(PROFILE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return EmployeeProfile(**data)
    except:
        return None


def delete_profile():
    if os.path.exists(PROFILE_FILE):
        os.remove(PROFILE_FILE)


def save_menu(menu: WeeklyMenu):
    with open(MENU_FILE, 'w', encoding='utf-8') as f:
        json.dump(menu.model_dump(), f, ensure_ascii=False, indent=2, default=str)


def load_menu() -> WeeklyMenu | None:
    if not os.path.exists(MENU_FILE):
        return None
    try:
        with open(MENU_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return WeeklyMenu(**data)
    except:
        return None


def save_avatar_path(path: str):
    """Копирует изображение в локальное хранилище и сохраняет путь."""
    import shutil
    if os.path.exists(path):
        shutil.copy(path, AVATAR_FILE)
    # Сохраняем путь в файл настроек (пока не используется, можно вернуть AVATAR_FILE)


def get_avatar_path() -> str:
    return AVATAR_FILE if os.path.exists(AVATAR_FILE) else ""


def delete_menu():
    if os.path.exists(MENU_FILE):
        os.remove(MENU_FILE)

