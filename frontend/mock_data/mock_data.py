"""
Мок-данные для MVP.
Эмулирует ответы сервера: авторизацию и получение недельного меню.
Привязка к реальному календарю – понедельник текущей недели.
"""

from datetime import date, timedelta
from shared_models.schemas import (
    AuthRequest, AuthResponse, EmployeeProfile,
    Dish, DayMenu, WeeklyMenu
)

# ---------- ПОЛЬЗОВАТЕЛИ (логин, пароль, профиль) ----------
MOCK_USERS = {
    "ivanov": {
        "password": "123456",
        "profile": EmployeeProfile(
            employee_id=101,
            full_name="Иванов Иван Иванович",
            position="Слесарь-ремонтник 4 разряда",
            plant="АО 'Тяжмаш', цех №3"
        )
    },
    "petrova": {
        "password": "654321",
        "profile": EmployeeProfile(
            employee_id=202,
            full_name="Петрова Анна Сергеевна",
            position="Оператор ЧПУ",
            plant="ООО 'МеталлПрофи', участок фрезеровки"
        )
    },
    "admin": {
        "password": "admin",
        "profile": EmployeeProfile(
            employee_id=0,
            full_name="Администратор Системы",
            position="Технолог питания",
            plant="Центральный офис"
        )
    }
}

# ---------- БЛЮДА (постоянный справочник) ----------
DISHES = {
    1: Dish(dish_id=1, name="Борщ со сметаной", category="первое", calories=250, proteins=12.0, fats=8.0, carbs=30.0, allergens=["сметана"]),
    2: Dish(dish_id=2, name="Суп-лапша куриная", category="первое", calories=210, proteins=14.0, fats=6.0, carbs=24.0, allergens=["глютен"]),
    3: Dish(dish_id=3, name="Котлета рубленая", category="второе", calories=380, proteins=28.0, fats=22.0, carbs=14.0, allergens=["глютен"]),
    4: Dish(dish_id=4, name="Рыба запечённая", category="второе", calories=310, proteins=35.0, fats=15.0, carbs=5.0, allergens=[]),
    5: Dish(dish_id=5, name="Каша гречневая", category="гарнир", calories=160, proteins=6.0, fats=3.0, carbs=30.0, allergens=[]),
    6: Dish(dish_id=6, name="Пюре картофельное", category="гарнир", calories=140, proteins=3.0, fats=4.0, carbs=25.0, allergens=["молоко"]),
    7: Dish(dish_id=7, name="Салат овощной", category="салат", calories=80, proteins=2.0, fats=5.0, carbs=7.0, allergens=[]),
    8: Dish(dish_id=8, name="Компот из сухофруктов", category="напиток", calories=90, proteins=0.5, fats=0.0, carbs=22.0, allergens=[]),
    9: Dish(dish_id=9, name="Хлеб ржаной", category="хлеб", calories=180, proteins=6.0, fats=1.0, carbs=38.0, allergens=["глютен"]),
}

# ---------- ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ: получить понедельник текущей недели ----------
def _get_current_monday() -> date:
    today = date.today()
    return today - timedelta(days=today.weekday())

# ---------- ФОРМИРОВАНИЕ МЕНЮ НА ТЕКУЩУЮ НЕДЕЛЮ ----------
def _generate_weekly_menu() -> WeeklyMenu:
    """Генерирует меню с понедельника по воскресенье."""
    monday = _get_current_monday()
    days = []
    weekdays_ru = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

    # Наборы блюд на обед (с понедельника по пятницу – рабочие дни, суббота/воскресенье – выходные)
    week_menu_config = {
        0: [1, 3, 5, 7, 8, 9],   # пн: борщ, котлета, гречка, салат, компот, хлеб
        1: [2, 4, 6, 7, 8, 9],   # вт: суп-лапша, рыба, пюре, салат, компот, хлеб
        2: [1, 3, 5, 7, 8, 9],   # ср: аналогично пн
        3: [2, 4, 5, 7, 8, 9],   # чт: суп-лапша, рыба, гречка, салат, компот, хлеб
        4: [1, 3, 6, 7, 8, 9],   # пт: борщ, котлета, пюре, салат, компот, хлеб
        5: [],                    # сб: выходной
        6: [],                    # вс: выходной
    }

    summary_texts = {
        0: "Сегодня борщ и котлета — сбалансированный обед для тяжёлой физической работы. Борщ богат клетчаткой, котлета — белком для мышц. Гречка даёт медленные углеводы, салат — витамины.",
        1: "Рыба запечённая — лёгкий источник омега-3 и белка, хорошо подходит для поддержания концентрации после обеда. Суп-лапша восполняет жидкость, пюре — быстрые углеводы.",
        2: "Повторение понедельника: классический набор, проверенный временем. Белково-углеводный баланс для активного труда.",
        3: "Четверг — рыбный день. Рыба и гречка — диетическое сочетание, не вызывает сонливости. Суп-лапша и салат дополняют рацион.",
        4: "Пятница — завершаем неделю сытным обедом: борщ и котлета с пюре. Углеводное окно закрыто, можно работать до конца смены.",
        5: "Выходной день. Отдыхайте и питайтесь дома!",
        6: "Воскресенье — выходной. Приятного аппетита за семейным столом.",
    }

    for i in range(7):
        day_date = monday + timedelta(days=i)
        dish_ids = week_menu_config[i]
        dishes = [DISHES[did] for did in dish_ids]
        is_weekend = (day_date.weekday() >= 5)  # 5-суббота, 6-воскресенье

        day_menu = DayMenu(
            date=day_date,
            weekday=weekdays_ru[i],
            is_weekend=is_weekend,
            dishes=dishes,
            summary=summary_texts[i]
        )
        days.append(day_menu)

    return WeeklyMenu(
        days=days,
        last_updated=date.today()
    )

# ---------- ИНТЕРФЕЙСНЫЕ ФУНКЦИИ (имитация API) ----------
def mock_login(username: str, password: str) -> AuthResponse:
    """Имитация POST /auth/login"""
    if username not in MOCK_USERS:
        raise ValueError("Неверный логин или пароль")
    user_data = MOCK_USERS[username]
    if password != user_data["password"]:
        raise ValueError("Неверный логин или пароль")

    # Генерируем фейковый JWT (в реальности токен приходит с сервера)
    token = f"fake-jwt-{username}-{date.today().isoformat()}"
    return AuthResponse(
        token=token,
        profile=user_data["profile"]
    )

def mock_fetch_menu(token: str) -> WeeklyMenu:
    """Имитация GET /menu?week=current"""
    # Проверка токена (простая проверка наличия строки "fake-jwt")
    if not token.startswith("fake-jwt-"):
        raise ValueError("Недействительный токен")
    return _generate_weekly_menu()

def mock_fetch_profile(token: str) -> EmployeeProfile:
    """Имитация GET /profile"""
    # В MVP профиль храним локально после логина,
    # но для демонстрации можно извлечь из токена
    try:
        username = token.split("-")[2]  # fake-jwt-username-...
        return MOCK_USERS[username]["profile"]
    except (IndexError, KeyError):
        raise ValueError("Недействительный токен")