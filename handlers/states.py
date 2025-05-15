from aiogram.fsm.state import StatesGroup, State

class OperatorStates(StatesGroup):
    waiting_question = State()      # Ожидание вопроса пользователя
    operator_typing = State()       # Оператор печатает ответ
    user_waiting = State()          # Пользователь ждет ответа