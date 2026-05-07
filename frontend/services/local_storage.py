"""
Локальное хранилище для кэширования данных между сессиями.
Работает и на десктопе, и на Android.
"""

import json
import os
from datetime import date
from shared_models.schemas import EmployeeProfile, WeeklyMenu
from kivy.app import App

# ---------- ленивая инициализация путей ----------
def _get_user_data_dir():
    """Возвращает директорию, доступную для записи. На Android использует user_data_dir."""
    try:
        app = App.get_running_app()
        if app is not None:
            return os.path.join(app.user_data_dir, 'user_data')
    except:
        pass
    # на десктопе (или если приложение ещё не создано) используем папку рядом с этим файлом
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'user_data')

def _get_base_path(filename):
    _dir = _get_user_data_dir()
    os.makedirs(_dir, exist_ok=True)
    return os.path.join(_dir, filename)

def _token_file():    return _get_base_path('token.json')
def _profile_file():  return _get_base_path('profile.json')
def _menu_file():     return _get_base_path('menu.json')
def _avatar_file():   return _get_base_path('avatar.png')

# ---------- сохранение / загрузка ----------
def save_token(token: str):
    with open(_token_file(), 'w', encoding='utf-8') as f:
        json.dump({'token': token, 'saved_at': str(date.today())}, f)

def load_token() -> str | None:
    path = _token_file()
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('token')
    except:
        return None

def delete_token():
    path = _token_file()
    if os.path.exists(path):
        os.remove(path)

def save_profile(profile: EmployeeProfile):
    if hasattr(profile, 'model_dump'):
        data = profile.model_dump()
    else:
        data = profile.dict()
    print(f"Сохраняю профиль: {data} в {_profile_file()}")
    with open(_profile_file(), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_profile() -> EmployeeProfile | None:
    path = _profile_file()
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return EmployeeProfile(**data)
    except:
        return None

def delete_profile():
    path = _profile_file()
    if os.path.exists(path):
        os.remove(path)

def save_menu(menu: WeeklyMenu):
    if hasattr(menu, 'model_dump'):
        data = menu.model_dump()
    else:
        data = menu.dict()
    with open(_menu_file(), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

def load_menu() -> WeeklyMenu | None:
    path = _menu_file()
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return WeeklyMenu(**data)
    except:
        return None

def delete_menu():
    path = _menu_file()
    if os.path.exists(path):
        os.remove(path)

def save_avatar_path(source_path: str):
    """Копирует изображение в локальное хранилище."""
    import shutil
    if os.path.exists(source_path):
        shutil.copy(source_path, _avatar_file())

def get_avatar_path() -> str:
    path = _avatar_file()
    return path if os.path.exists(path) else ""