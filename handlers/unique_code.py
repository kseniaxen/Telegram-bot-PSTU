from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from filters import FSMContextFilter
from utils import load_texts
from utils import CASE_DATA
from keyboards import main_menu

TEXTS = load_texts()
router = Router()


class FormStates:
    waiting_for_case_number = "waiting_for_case_number"


@router.message(F.text == TEXTS["buttons"]["unique_code"])
async def unique_code_message(message: types.Message, state: FSMContext):
    await state.set_state(FormStates.waiting_for_case_number)
    await message.answer(
        TEXTS["unique_code"]["title"],
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(F.text.regexp(r'^\d+$'), FSMContextFilter(state=FormStates.waiting_for_case_number))
async def handle_case_number(message: types.Message, state: FSMContext):
    # Удаляем ведущие нули и проверяем номер
    case_number = message.text.lstrip('0') or '0'

    if not case_number:
        await message.answer(TEXTS["unique_code"]["data"][1]["not_found"], reply_markup=main_menu)
        await state.clear()
        return

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

    await state.clear()


@router.message()
async def handle_invalid_input(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == FormStates.waiting_for_case_number:
        await message.answer(TEXTS["unique_code"]["data"][2]["invalid_input"])
    elif message.text != TEXTS["buttons"]["unique_code"]:
        await message.answer("Пожалуйста, выберите действие из меню", reply_markup=main_menu)