from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import Config
from handlers import base, specialties, sections, operator

# Инициализация хранилища состояний
storage = MemoryStorage()
bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher(storage=storage)

# Подключение роутеров
dp.include_routers(
    base.router,
    specialties.router,
    sections.router,
    operator.router
)

if __name__ == "__main__":
    dp.run_polling(bot)