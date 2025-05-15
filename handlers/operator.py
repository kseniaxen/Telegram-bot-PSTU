from aiogram import Router, types, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from config import Config
from .states import OperatorStates
from utils import load_texts

TEXTS = load_texts()
router = Router()

# Временное хранилище для вопросов пользователей
user_questions = {}


@router.message(F.text == TEXTS["buttons"]["operator"])
async def request_operator(message: types.Message, state: FSMContext):
    """Начало диалога с оператором"""
    await message.answer(
        "Опишите ваш вопрос оператору в одном сообщении:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(OperatorStates.waiting_question)
    await state.update_data(start_time=message.date.timestamp())


@router.message(OperatorStates.waiting_question)
async def process_user_question(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка вопроса пользователя"""
    data = await state.get_data()
    wait_time = int(message.date.timestamp() - data['start_time'])

    # Сохраняем вопрос во временном хранилище
    user_questions[message.from_user.id] = {
        "question": message.text,
        "start_time": data['start_time']
    }

    # Получаем имя пользователя или используем user_id, если username отсутствует
    username = message.from_user.username or f"ID: {message.from_user.id}"

    msg = await bot.send_message(
        chat_id=Config.OPERATOR_CHAT_ID,
        text=f"❓ Новый вопрос:\n"
             f"👤 От: @{username} (ID: {message.from_user.id})\n"
             f"⏱ Ожидал: {wait_time} сек.\n"
             f"✉️ Вопрос: {message.text}\n\n"
             f"Ответьте на это сообщение, чтобы написать пользователю",
        reply_markup=types.ForceReply(selective=True)
    )

    # Сохраняем message_id для связи
    await state.update_data(operator_message_id=msg.message_id)

    await message.answer("Ваш вопрос принят! Оператор ответит вам в этом чате.")
    await state.set_state(OperatorStates.user_waiting)


@router.message(OperatorStates.user_waiting)
async def notify_user_waiting(message: types.Message):
    """Уведомление, что пользователь уже ждет ответа"""
    await message.answer("Вы уже отправили вопрос оператору. Пожалуйста, дождитесь ответа.")


@router.message(
    F.reply_to_message,  # Проверяем, что это ответ на сообщение
    F.from_user.id == Config.OPERATOR_CHAT_ID,  # Проверяем, что от оператора
    F.reply_to_message.from_user.id == Config.BOT_ID  # Проверяем, что ответ на сообщение бота
)
async def handle_operator_reply(message: types.Message, bot: Bot):
    """Обработка ответа оператора"""
    original_text = message.reply_to_message.text

    # Ищем ID пользователя в тексте сообщения
    user_id = None
    for line in original_text.split('\n'):
        if line.startswith("👤 От: @") and "(ID:" in line:
            user_id = int(line.split("(ID:")[1].split(")")[0].strip())
            break

    if not user_id:
        await message.answer("❌ Не удалось определить пользователя для ответа.")
        return

    # Отправляем ответ пользователю
    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"📩 Ответ оператора:\n\n{message.text}"
        )
        await message.answer("✅ Ответ успешно отправлен пользователю")

        # Очищаем данные вопроса
        if user_id in user_questions:
            del user_questions[user_id]

    except Exception as e:
        await message.answer(f"❌ Ошибка при отправке ответа: {str(e)}")