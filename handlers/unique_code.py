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
    waiting_for_full_name = "waiting_for_full_name"


@router.message(F.text == TEXTS["buttons"]["unique_code"])
async def unique_code_message(message: types.Message, state: FSMContext):
    await state.set_state(FormStates.waiting_for_full_name)
    await message.answer(
        TEXTS["unique_code"]["title"],
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(FSMContextFilter(state=FormStates.waiting_for_full_name))
async def handle_full_name(message: types.Message, state: FSMContext):
    input_name = message.text.strip()
    normalized_input = normalize_name(input_name)

    found_cases = []

    for unique_code, data in CASE_DATA.items():
        db_name = normalize_name(data['ФизическоеЛицо'])

        # Проверяем полное совпадение
        if normalized_input == db_name:
            found_cases.append((unique_code, data))
            break

    if found_cases:
        _, data = found_cases[0]
        await message.answer(
            TEXTS["unique_code"]["data"][0]["success"].format(
                name=data['ФизическоеЛицо'],
                unique_code=data['УникальныйКод']
            ),
            reply_markup=main_menu
        )
    else:
        await message.answer(
            TEXTS["unique_code"]["data"][1]["not_found"],
            reply_markup=main_menu
        )

    await state.clear()


def normalize_name(name: str) -> str:
    return ' '.join(name.split()).lower()


@router.message()
async def handle_invalid_input(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == FormStates.waiting_for_full_name:
        await message.answer("Пожалуйста, введите ФИО полностью, как в документах")
    elif message.text != TEXTS["buttons"]["unique_code"]:
        await message.answer("Пожалуйста, выберите действие из меню", reply_markup=main_menu)