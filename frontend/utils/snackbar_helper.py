from kivymd.uix.snackbar import Snackbar

def show_snackbar(text: str, duration: float = 1.5):
    """Показать снекбар (KivyMD 1.2.0)."""
    snack = Snackbar(duration=duration)
    snack.text = text
    snack.open()