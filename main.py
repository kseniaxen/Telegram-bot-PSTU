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

# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=TEXTS["buttons"]["specialties"]), KeyboardButton(text=TEXTS["buttons"]["documents"])],
        [KeyboardButton(text=TEXTS["buttons"]["deadlines"]), KeyboardButton(text=TEXTS["buttons"]["site"])],
        [KeyboardButton(text=TEXTS["buttons"]["schedule"]), KeyboardButton(text=TEXTS["buttons"]["contacts"])],
        [KeyboardButton(text=TEXTS["buttons"]["operator"])]
    ],
    resize_keyboard=True
)

# Меню направлений подготовки
specialties_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=TEXTS["buttons"]["bachelor"]), KeyboardButton(text=TEXTS["buttons"]["specialist"])],
        [KeyboardButton(text=TEXTS["buttons"]["master"]), KeyboardButton(text=TEXTS["buttons"]["aspirantura"])],
        [KeyboardButton(text=TEXTS["buttons"]["back"])]
    ],
    resize_keyboard=True
)

# Список всех кнопок меню
all_menu_buttons = [
    TEXTS["buttons"]["specialties"],
    TEXTS["buttons"]["documents"],
    TEXTS["buttons"]["deadlines"],
    TEXTS["buttons"]["site"],
    TEXTS["buttons"]["schedule"],
    TEXTS["buttons"]["contacts"],
    TEXTS["buttons"]["operator"],
    TEXTS["buttons"]["bachelor"],
    TEXTS["buttons"]["specialist"],
    TEXTS["buttons"]["master"],
    TEXTS["buttons"]["aspirantura"],
    TEXTS["buttons"]["back"]
]

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

#График работы
@router.message(lambda msg: msg.text == TEXTS["buttons"]["schedule"])
async def show_schedule(message: types.Message):
    response = (
            f"{TEXTS["schedule"]["title"]}\n\n" +
            "\n".join(f"{schedule}" for schedule in TEXTS["schedule"]["data"]) +
            f"\n\n{TEXTS["schedule"]["extra"]}"
    )
    await message.answer(response, parse_mode="HTML")

#Документы
@router.message(lambda msg: msg.text == TEXTS["buttons"]["documents"])
async def show_documents(message: types.Message):
    response = (
            f"{TEXTS["documents"]["title"]}\n\n" +
            "\n".join(f"{document}" for document in TEXTS["documents"]["data"]) +
            f"\n\n{TEXTS["documents"]["extra"]}"
    )
    await message.answer(response, parse_mode="HTML")

#Контакты
@router.message(lambda msg: msg.text == TEXTS["buttons"]["contacts"])
async def show_contacts(message: types.Message):
    response = (
            f"{TEXTS['contacts']['title']}\n\n" +
            "\n".join(
                f"{contact['name']}\n{contact['value']}"
                for contact in TEXTS["contacts"]["data"]
            ) +
            f"\n\n{TEXTS['contacts']['extra']}"
    )
    await message.answer(response, parse_mode="HTML")

#Сайт
@router.message(lambda msg: msg.text == TEXTS["buttons"]["site"])
async def show_website(message: types.Message):
    response = (
            f"{TEXTS["site"]["title"]}\n\n" +
            "\n".join(f"{site}" for site in TEXTS["site"]["data"]) +
            f"\n\n{TEXTS["site"]["extra"]}"
    )
    await message.answer(response, parse_mode="HTML")

#Сроки приема
@router.message(lambda msg: msg.text == TEXTS["buttons"]["deadlines"])
async def show_deadlines(message: types.Message):
    deadlines = TEXTS["deadlines"]
    programs = [f"<b>{item['name']}:</b> {item['dates']}" for item in deadlines["data"]]

    response = (
            f"{deadlines['title']}\n\n" +
            "\n".join(f"• {program}" for program in programs) +
            f"\n\n{deadlines['extra']}"
    )
    await message.answer(response, parse_mode="HTML")

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