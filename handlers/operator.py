from aiogram import Router, types, Bot, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from config import Config
from .states import OperatorStates
from utils import load_texts

TEXTS = load_texts()
router = Router()

# Хранилище вопросов: {user_id: {"support_msg_id": int, "question": str, "username": str}}
user_questions = {}


@router.message(F.text == TEXTS["buttons"]["operator"])
async def request_operator(message: types.Message, state: FSMContext):
    """Обработка нажатия кнопки 'Связаться с оператором'"""
    await message.answer(
        "📝 Пожалуйста, опишите ваш вопрос в одном сообщении:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(OperatorStates.waiting_question)
    await state.update_data(start_time=message.date.timestamp())


@router.message(OperatorStates.waiting_question)
async def process_user_question(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка вопроса от пользователя"""
    user_data = await state.get_data()
    wait_time = int(message.date.timestamp() - user_data['start_time'])

    username = message.from_user.username or f"ID: {message.from_user.id}"

    try:
        # Создаем клавиатуру с кнопками
        keyboard = InlineKeyboardBuilder()
        keyboard.add(
            types.InlineKeyboardButton(
                text="📨 Ответить",
                callback_data=f"answer_{message.from_user.id}"
            ),
            types.InlineKeyboardButton(
                text="❌ Закрыть",
                callback_data=f"close_{message.from_user.id}"
            )
        )
        keyboard.adjust(2)  # Располагаем кнопки в 2 колонки

        # Отправляем вопрос в чат поддержки
        support_msg = await bot.send_message(
            chat_id=Config.SUPPORT_TEAM_CHAT_ID,
            text=f"🔔 Новый вопрос от пользователя:\n"
                 f"👤 Имя: @{username}\n"
                 f"🆔 ID: {message.from_user.id}\n"
                 f"⏳ Время ожидания: {wait_time} сек.\n"
                 f"❓ Вопрос:\n{message.text}",
            reply_markup=keyboard.as_markup()
        )

        # Сохраняем связь между сообщением в поддержке и пользователем
        user_questions[message.from_user.id] = {
            "support_msg_id": support_msg.message_id,
            "question": message.text,
            "username": username,
            "user_id": message.from_user.id
        }

        await message.answer("✅ Ваш вопрос передан оператору! Ожидайте ответа здесь.")
        await state.set_state(OperatorStates.user_waiting)

    except Exception as e:
        await message.answer("❌ Произошла ошибка при отправке вопроса. Пожалуйста, попробуйте позже.")
        await state.clear()


@router.callback_query(F.data.startswith("answer_"))
async def handle_answer_callback(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    """Обработка нажатия кнопки 'Ответить'"""
    user_id = int(callback.data.split("_")[1])

    if user_id not in user_questions:
        await callback.answer("❌ Вопрос уже был обработан или удален", show_alert=True)
        return

    # Сохраняем данные для ответа
    await state.set_state(OperatorStates.operator_typing)
    await state.update_data(
        target_user_id=user_id,
        original_message_id=callback.message.message_id
    )

    # Просим оператора ввести ответ
    await callback.message.edit_reply_markup()  # Удаляем кнопки
    await callback.message.answer(
        f"✍️ Введите ответ для пользователя:\n"
        f"👤 @{user_questions[user_id]['username']} (ID: {user_id})\n"
        f"❓ Вопрос: {user_questions[user_id]['question']}\n\n"
        f"Отправьте текст ответа:",
        reply_markup=types.ForceReply(selective=True)
    )

    await callback.answer()


@router.callback_query(F.data.startswith("close_"))
async def handle_close_callback(callback: types.CallbackQuery, bot: Bot):
    """Обработка нажатия кнопки 'Закрыть' с уведомлением пользователя"""
    operator_name = callback.from_user.full_name
    user_id = int(callback.data.split("_")[1])

    if user_id not in user_questions:
        await callback.answer("❌ Вопрос уже был обработан", show_alert=True)
        return

    try:
        question_data = user_questions[user_id]

        # 1. Уведомляем пользователя
        try:
            await bot.send_message(
                chat_id=user_id,
                text=f"ℹ️ Ваш вопрос был закрыт оператором:\n\n"
                     f"❓ Вопрос: {question_data['question']}\n\n"
                     f"Если вам нужна дополнительная помощь, "
                     f"вы можете задать новый вопрос."
            )
        except Exception:
            pass  # Без уведомления об ошибке

        # 2. Редактируем сообщение в чате поддержки
        await callback.message.edit_text(
            text=f"❌ Вопрос закрыт оператором {operator_name}\n\n"
                 f"👤 Пользователь: @{question_data['username']}\n"
                 f"🆔 ID: {user_id}\n"
                 f"❓ Вопрос: {question_data['question']}",
            reply_markup=None
        )

        # 3. Удаляем запись о вопросе
        del user_questions[user_id]

        # 4. Уведомляем оператора
        await callback.answer("Вопрос закрыт", show_alert=False)

        # 5. Отправляем подтверждение оператору
        await callback.message.answer(
            f"✅ Вы закрыли вопрос пользователя @{question_data['username']}",
            reply_to_message_id=callback.message.message_id
        )

    except Exception:
        await callback.answer("Произошла ошибка при закрытии вопроса", show_alert=True)


@router.message(OperatorStates.user_waiting)
async def notify_user_waiting(message: types.Message):
    """Уведомление, если пользователь уже ждет ответа"""
    await message.answer("⏳ Вы уже отправили вопрос оператору. Пожалуйста, дождитесь ответа.")


@router.message(OperatorStates.operator_typing)
async def handle_operator_reply(message: types.Message, state: FSMContext, bot: Bot):
    """Обработка ответа оператора"""
    data = await state.get_data()
    user_id = data['target_user_id']

    if user_id not in user_questions:
        await message.answer("❌ Ошибка: вопрос больше не актуален")
        await state.clear()
        return

    try:
        #Отправляем ответ пользователю
        await bot.send_message(
            chat_id=user_id,
            text=f"📩 Ответ от поддержки:\n\n{message.text}\n\n"
                 f"Если у вас остались вопросы, напишите нам снова."
        )

        #Редактируем исходное сообщение в чате поддержки (без создания нового)
        question_data = user_questions[user_id]
        await bot.edit_message_text(
            chat_id=Config.SUPPORT_TEAM_CHAT_ID,
            message_id=question_data['support_msg_id'],
            text=f"✅ Ответ отправлен пользователю @{question_data['username']}\n"
                 f"👤 Исходный вопрос:\n{question_data['question']}\n\n"
                 f"📩 Ответ оператора:\n{message.text}",
            reply_markup=None  # Удаляем кнопки
        )

        #Удаляем запись о вопросе
        del user_questions[user_id]

        #Подтверждение оператору (только ему, не в группу)
        await message.answer(
            f"✔️ Ответ успешно доставлен пользователю @{question_data['username']}",
            reply_markup=ReplyKeyboardRemove()
        )

    except Exception as e:
        error_msg = "❌ Не удалось отправить ответ: "
        if "bot was blocked" in str(e).lower():
            error_msg += "пользователь заблокировал бота"
            # Помечаем вопрос как неактивный
            if user_id in user_questions:
                question_data = user_questions[user_id]
                await bot.edit_message_text(
                    chat_id=Config.SUPPORT_TEAM_CHAT_ID,
                    message_id=question_data['support_msg_id'],
                    text=f"❌ Пользователь заблокировал бота\n\n"
                         f"👤 Исходный вопрос:\n{question_data['question']}",
                    reply_markup=None
                )
                del user_questions[user_id]
        elif "chat not found" in str(e).lower():
            error_msg += "чат с пользователем не найден"
        else:
            error_msg += str(e)

        await message.answer(error_msg)

    await state.clear()