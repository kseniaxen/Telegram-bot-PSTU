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

#Начало работы
@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer(TEXTS["hello"], reply_markup=main_menu, parse_mode="HTML")

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

#Связь с оператором
@router.message(lambda msg: msg.text == "👨‍💼 Связаться с оператором")
async def contact_operator(message: types.Message):
    await bot.send_message(
        #chat_id=int(os.getenv("OPERATOR_CHAT_ID")),
        text=f"Новый запрос от @{message.from_user.username}:\nID: {message.from_user.id}"
    )
    await message.answer("Ваш запрос передан оператору. Ожидайте ответа здесь.")

#Проверка сообщений
@router.message()
async def handle_text_input(message: types.Message):
    if not message.text.startswith('/') and message.text not in main_menu:
        await message.answer(
            "Пожалуйста, выберите действие из меню ниже:",
            reply_markup=main_menu
        )

if __name__ == "__main__":
    dp.run_polling(bot)