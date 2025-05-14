from aiogram import Router, types
from aiogram.filters import Command
from keyboards import main_menu
from utils import load_texts

TEXTS = load_texts()
router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer(TEXTS["start"], reply_markup=main_menu, parse_mode="HTML")

@router.message(lambda msg: msg.text == TEXTS["buttons"]["back"])
async def back_to_main_menu(message: types.Message):
    await start(message)