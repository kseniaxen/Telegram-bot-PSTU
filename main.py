import os
import json
from pathlib import Path
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

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=TEXTS["menu"]["specialties"]), KeyboardButton(text=TEXTS["menu"]["documents"])],
        [KeyboardButton(text=TEXTS["menu"]["deadlines"]), KeyboardButton(text=TEXTS["menu"]["site"])],
        [KeyboardButton(text=TEXTS["menu"]["schedule"]), KeyboardButton(text=TEXTS["menu"]["contacts"])],
        [KeyboardButton(text=TEXTS["menu"]["operator"])]
    ],
    resize_keyboard=True
)

# Меню направлений подготовки
specialties_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=TEXTS["specialties"]["menu"]["bachelor"]), KeyboardButton(text=TEXTS["specialties"]["menu"]["specialist"])],
        [KeyboardButton(text=TEXTS["specialties"]["menu"]["master"]), KeyboardButton(text=TEXTS["specialties"]["menu"]["aspirantura"])],
        [KeyboardButton(text="⬅️ Назад")]
    ],
    resize_keyboard=True
)

# Список всех кнопок меню
all_menu_buttons = [
    TEXTS["menu"]["specialties"],
    TEXTS["menu"]["documents"],
    TEXTS["menu"]["deadlines"],
    TEXTS["menu"]["site"],
    TEXTS["menu"]["schedule"],
    TEXTS["menu"]["contacts"],
    TEXTS["menu"]["operator"],
    TEXTS["specialties"]["menu"]["bachelor"],
    TEXTS["specialties"]["menu"]["specialist"],
    TEXTS["specialties"]["menu"]["master"],
    TEXTS["specialties"]["menu"]["aspirantura"],
    "⬅️ Назад"
]

#Начало работы
@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer(TEXTS["hello"], reply_markup=main_menu, parse_mode="HTML")

#Список направлений подготовки
@router.message(lambda msg: msg.text == TEXTS["menu"]["specialties"])
async def show_specialties_menu(message: types.Message):
    await message.answer(TEXTS["specialties"]["name"], reply_markup=specialties_menu, parse_mode="HTML")

#Меню направлений подготовки
@router.message(lambda msg: msg.text in [
    TEXTS["specialties"]["menu"]["bachelor"],
    TEXTS["specialties"]["menu"]["specialist"],
    TEXTS["specialties"]["menu"]["master"],
    TEXTS["specialties"]["menu"]["aspirantura"]
])
async def handle_specialties(message: types.Message):
    match message.text:
        case text if text == TEXTS["specialties"]["menu"]["bachelor"]:
            response = "Бакалавр"
        case text if text == TEXTS["specialties"]["menu"]["specialist"]:
            response = "Специалист"
        case text if text == TEXTS["specialties"]["menu"]["master"]:
            response = "Магистратура"
        case text if text == TEXTS["specialties"]["menu"]["aspirantura"]:
            response = "Аспирантура"
        case _:
            response = "Неизвестная команда"
    await message.answer(response, reply_markup=specialties_menu, parse_mode="HTML")

#Назад
@router.message(lambda msg: msg.text == "⬅️ Назад")
async def back_to_main_menu(message: types.Message):
    await start(message)

#График работы
@router.message(lambda msg: msg.text == TEXTS["menu"]["schedule"])
async def show_schedule(message: types.Message):
    await message.answer(TEXTS["main"]["schedule"], parse_mode="HTML")

#Документы
@router.message(lambda msg: msg.text == TEXTS["menu"]["documents"])
async def show_documents(message: types.Message):
    await message.answer(TEXTS["main"]["documents"], parse_mode="HTML")

#Контакты
@router.message(lambda msg: msg.text == TEXTS["menu"]["contacts"])
async def show_contacts(message: types.Message):
    await message.answer(TEXTS["main"]["contacts"], parse_mode="HTML")

#Сайт
@router.message(lambda msg: msg.text == TEXTS["menu"]["site"])
async def show_website(message: types.Message):
    await message.answer(TEXTS["main"]["site"], parse_mode="HTML")

#Сроки приема
@router.message(lambda msg: msg.text == TEXTS["menu"]["deadlines"])
async def show_deadlines(message: types.Message):
    await message.answer(TEXTS["main"]["deadlines"], parse_mode="HTML")

#Связь с оператором
@router.message(lambda msg: msg.text == TEXTS["menu"]["operator"])
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