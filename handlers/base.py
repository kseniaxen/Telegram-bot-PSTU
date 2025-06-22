from aiogram import Router, types
from aiogram.filters import Command
from keyboards import main_menu
from utils import load_texts
from aiogram.types import ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from .states import OperatorStates

TEXTS = load_texts()
router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer(TEXTS["start"], reply_markup=main_menu, parse_mode="HTML")
'''
@router.message(Command("question"))
async def question_handler(message: types.Message, state: FSMContext):
    """Обработка /question — сразу запрашивает вопрос"""
    await message.answer(
        TEXTS["operator"]["title"],
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(OperatorStates.waiting_question)
    await state.update_data(start_time=message.date.timestamp())
'''

@router.message(lambda msg: msg.text == TEXTS["buttons"]["back"])
async def back_to_main_menu(message: types.Message):
    await start(message)