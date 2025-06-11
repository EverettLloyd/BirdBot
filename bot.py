# bot.py — точка входа в приложение
import asyncio
from aiogram import Bot, Dispatcher
from config import settings
from db import init_db
from handlers import main_menu, seeker_form, owner_form, admin_actions
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Инициализация бота и диспетчера
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

# Подключаем роутеры
dp.include_router(main_menu.router)
dp.include_router(seeker_form.router)
dp.include_router(owner_form.router)
dp.include_router(admin_actions.router)

# Основная асинхронная точка входа
async def main() -> None:
    await init_db()  # Инициализация базы данных
    await dp.start_polling(bot)

# Запуск
if __name__ == "__main__":
    asyncio.run(main())
