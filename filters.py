from aiogram.filters import Filter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

class FSMContextFilter(Filter):
    def __init__(self, state: str):
        self.state = state

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        current_state = await state.get_state()
        return current_state == self.state