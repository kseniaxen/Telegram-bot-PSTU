from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
import logging

from filters import FSMContextFilter
from utils import load_texts
from utils import CASE_DATA
from keyboards import main_menu

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='bot_actions.log',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

TEXTS = load_texts()
router = Router()


class FormStates:
    waiting_for_full_name = "waiting_for_full_name"


@router.message(F.text == TEXTS["buttons"]["unique_code"])
async def unique_code_message(message: types.Message, state: FSMContext):
    logger.info(f"User {message.from_user.id} ({message.from_user.username}) started unique_code flow")
    await state.set_state(FormStates.waiting_for_full_name)
    await message.answer(
        TEXTS["unique_code"]["title"],
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(FSMContextFilter(state=FormStates.waiting_for_full_name))
async def handle_full_name(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    input_name = message.text.strip()

    logger.info(f"User {user_id} ({username}) entered name: {input_name}")

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
        response = TEXTS["unique_code"]["data"][0]["success"].format(
            name=data['ФизическоеЛицо'],
            unique_code=data['УникальныйКод']
        )
        logger.info(f"User {user_id} ({username}) found case: {data['УникальныйКод']}")
        await message.answer(
            response,
            reply_markup=main_menu
        )
    else:
        logger.warning(f"User {user_id} ({username}) name not found in database")
        await message.answer(
            TEXTS["unique_code"]["data"][1]["not_found"],
            reply_markup=main_menu
        )

    await state.clear()


def normalize_name(name: str) -> str:
    return ' '.join(name.split()).lower()


@router.message()
async def handle_invalid_input(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    current_state = await state.get_state()

    if current_state == FormStates.waiting_for_full_name:
        logger.warning(f"User {user_id} ({username}) sent invalid input during name entry: {message.text}")
        await message.answer("Пожалуйста, введите ФИО полностью, как в документах")
    elif message.text != TEXTS["buttons"]["unique_code"]:
        logger.warning(f"User {user_id} ({username}) sent unexpected message: {message.text}")
        await message.answer("Пожалуйста, выберите действие из меню", reply_markup=main_menu)