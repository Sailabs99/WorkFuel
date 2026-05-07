"""
API-клиент для взаимодействия с реальным бэкендом.
"""

import requests
from shared_models.schemas import AuthRequest, AuthResponse, WeeklyMenu
from config import API_BASE_URL


class ApiClient:
    def login(self, username: str, password: str) -> AuthResponse:
        url = f"{API_BASE_URL}/auth/login"
        auth_req = AuthRequest(username=username, password=password)
        payload = auth_req.model_dump() if hasattr(auth_req, 'model_dump') else auth_req.dict()
        try:
            resp = requests.post(url, json=payload, timeout=10)
            resp.raise_for_status()
            print("Отправка запроса на", url)
            print("Статус ответа:", resp.status_code)
            print("Тело ответа:", resp.text)
            return AuthResponse(**resp.json())
        except requests.RequestException as e:
            raise ConnectionError(f"Ошибка связи с сервером: {e}")
        except Exception as e:
            raise ValueError(f"Ошибка обработки ответа: {e}")

    def fetch_weekly_menu(self, token: str) -> WeeklyMenu:
        url = f"{API_BASE_URL}/menu/weekly"
        headers = {"Authorization": f"Bearer {token}"}   # <-- исправлено
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            return WeeklyMenu(**resp.json())
        except requests.RequestException as e:
            raise ConnectionError(f"Ошибка связи с сервером: {e}")
        except Exception as e:
            raise ValueError(f"Ошибка обработки ответа: {e}")