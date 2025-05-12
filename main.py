import os
import json
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

load_dotenv()

bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
router = Router()
dp.include_router(router)

with open("text.json", "r", encoding="utf-8") as file:
    TEXTS = json.load(file)

button_keys = {
    "main_menu": ["specialties", "documents", "deadlines", "site", "schedule", "contacts", "operator"],
    "specialties_menu": ["bachelor", "specialist", "master", "aspirantura", "back"]
}

def create_menu(buttons: list, buttons_per_row: int = 2) -> ReplyKeyboardMarkup:
    keyboard = []
    for i in range(0, len(buttons), buttons_per_row):
        row = buttons[i:i + buttons_per_row]
        keyboard.append([KeyboardButton(text=TEXTS["buttons"][btn]) for btn in row])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# Создаем все меню
main_menu = create_menu(button_keys["main_menu"])
specialties_menu = create_menu(button_keys["specialties_menu"])

# Список всех кнопок меню
all_menu_buttons = [TEXTS["buttons"][key] for menu in button_keys.values() for key in menu]

#Начало работы
@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer(TEXTS["start"], reply_markup=main_menu, parse_mode="HTML")

#Список направлений подготовки
@router.message(lambda msg: msg.text == TEXTS["buttons"]["specialties"])
async def show_specialties_menu(message: types.Message):
    await message.answer(TEXTS["specialties"]["title"], reply_markup=specialties_menu, parse_mode="HTML")

#Меню направлений подготовки
@router.message(lambda msg: msg.text in [
    TEXTS["buttons"]["bachelor"],
    TEXTS["buttons"]["specialist"],
    TEXTS["buttons"]["master"],
    TEXTS["buttons"]["aspirantura"]
])
async def handle_specialties(message: types.Message):
    info = TEXTS["specialties"]["extra"]["info_main"]
    match message.text:
        case text if text == TEXTS["buttons"]["bachelor"]:
            programs = TEXTS["specialties"]["data"]["bachelor"]
            title = "🎓 <b>Программы бакалавриата:</b>"
        case text if text == TEXTS["buttons"]["specialist"]:
            programs = TEXTS["specialties"]["data"]["specialist"]
            title = "📚 <b>Программы специалитета:</b>"
        case text if text == TEXTS["buttons"]["master"]:
            programs = TEXTS["specialties"]["data"]["master"]
            title = "👨‍🎓 <b>Программы магистратуры:</b>"
        case text if text == TEXTS["buttons"]["aspirantura"]:
            programs = TEXTS["specialties"]["data"]["aspirantura"]
            title = "👨‍🔬 <b>Программы аспирантуры:</b>"
            info = TEXTS["specialties"]["extra"]["info_asp"]
        case _:
            await message.answer("Неизвестная команда", reply_markup=specialties_menu)
            return

    response = (
            f"{title}\n\n" +
            "\n".join(f"• {program}" for program in programs) +
            f"\n\n{info}"
    )

    await message.answer(
        response,
        reply_markup=specialties_menu,
        parse_mode="HTML",
        disable_web_page_preview=True
    )

#Назад
@router.message(lambda msg: msg.text == TEXTS["buttons"]["back"])
async def back_to_main_menu(message: types.Message):
    await start(message)

# Универсальный обработчик
async def send_section(message: types.Message, section_name: str):
    section = TEXTS[section_name]
    if "values" in section["data"]:
        content = "\n".join(section["data"]["values"])
    else:
        content = "\n".join(f"<b>{item['name']}:</b> {item['value']}" for item in section["data"])

    response = f"{section['title']}\n\n{content}"
    if section.get("extra"):
        response += f"\n\n{section['extra']}"
    await message.answer(response, parse_mode="HTML")

# Регистрация всех обработчиков
sections = ["documents", "schedule", "site", "contacts", "deadlines"]
for section in sections:
    @router.message(lambda msg, sec=section: msg.text == TEXTS["buttons"][sec])
    async def handler(message: types.Message, sec=section):
        await send_section(message, sec)

#Связь с оператором
@router.message(lambda msg: msg.text == TEXTS["buttons"]["operator"])
async def contact_operator(message: types.Message):
    await bot.send_message(
        chat_id=int(os.getenv("OPERATOR_CHAT_ID")),
        text=f"Новый запрос от @{message.from_user.username}:\nID: {message.from_user.id}"
    )
    await message.answer("Ваш запрос передан оператору. Ожидайте ответа здесь.")

# Общий обработчик
@router.message()
async def handle_text_input(message: types.Message):
    if not message.text.startswith('/') and message.text not in all_menu_buttons:
        await message.answer(TEXTS["check_message"], reply_markup=main_menu)

if __name__ == "__main__":
    dp.run_polling(bot)