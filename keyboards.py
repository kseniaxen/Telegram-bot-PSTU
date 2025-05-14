from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import Config
from utils import load_texts

TEXTS = load_texts()

def create_menu(buttons: list, buttons_per_row: int = 2) -> ReplyKeyboardMarkup:
    keyboard = []
    for i in range(0, len(buttons), buttons_per_row):
        row = buttons[i:i + buttons_per_row]
        keyboard.append([KeyboardButton(text=TEXTS["buttons"][btn]) for btn in row])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_all_menu_buttons() -> list[str]:
    return [TEXTS["buttons"][key] for menu in Config.BUTTON_KEYS.values() for key in menu]

# Создаём все меню один раз при инициализации
main_menu = create_menu(Config.BUTTON_KEYS["main_menu"])
specialties_menu = create_menu(Config.BUTTON_KEYS["specialties_menu"])