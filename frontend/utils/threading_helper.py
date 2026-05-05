"""
Утилиты для работы с потоками.
"""

import threading
from kivy.clock import Clock


def run_in_thread(callback_on_result, callback_on_error=None):
    """
    Декоратор для выполнения функции в отдельном потоке.
    После завершения вызывает callback_on_result в главном потоке
    с результатом функции. При ошибке вызывает callback_on_error
    с текстом ошибки.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            def target():
                try:
                    result = func(*args, **kwargs)
                    # Планируем вызов колбэка в главном потоке
                    Clock.schedule_once(lambda dt: callback_on_result(result))
                except Exception as e:
                    if callback_on_error:
                        Clock.schedule_once(lambda dt: callback_on_error(str(e)))
                    else:
                        # Если колбэк ошибки не задан, пробрасываем исключение в главный поток
                        Clock.schedule_once(lambda dt: (_ for _ in ()).throw(e))
            threading.Thread(target=target, daemon=True).start()
        return wrapper
    return decorator