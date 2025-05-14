from aiogram import Bot, Dispatcher
from handlers import base, specialties, sections, operator
from config import Config

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher()

# Подключаем все роутеры
dp.include_routers(
    base.router,
    specialties.router,
    sections.router,
    operator.router
)

if __name__ == "__main__":
    dp.run_polling(bot)