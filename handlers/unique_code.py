from aiogram import Router, types, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from utils import load_texts
from utils import CASE_DATA
from keyboards import main_menu

TEXTS = load_texts()
router = Router()

@router.message(F.text == TEXTS["buttons"]["unique_code"])
async def unique_code_message(message: types.Message, state: FSMContext):
    await message.answer(
        TEXTS["unique_code"]["title"],
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(F.text.regexp(r'^\d+$'))
async def handle_case_number(message: types.Message):
    case_number = message.text
    if case_number in CASE_DATA:
        data = CASE_DATA[case_number]
        await message.answer(
            TEXTS["unique_code"]["data"][0]["success"].format(
                case_number=case_number,
                unique_code=data['УникальныйКод']
            ),
            reply_markup=main_menu
        )
    else:
        await message.answer(TEXTS["unique_code"]["data"][1]["not_found"], reply_markup=main_menu)

@router.message()
async def handle_invalid_input(message: types.Message):
    if message.text != TEXTS["buttons"]["unique_code"]:
        await message.answer(TEXTS["unique_code"]["data"][2]["invalid_input"], reply_markup=main_menu)
