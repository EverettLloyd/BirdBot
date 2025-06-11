import asyncio

from aiogram import Bot, Dispatcher
from db import init_db

async def main() -> None:
    await init_db()
    await dp.start_polling(bot)

from config import settings
from handlers import main_menu, seeker_form, owner_form, admin_actions

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

# Регистрируем все роутеры
dp.include_router(main_menu.router)
dp.include_router(seeker_form.router)
dp.include_router(owner_form.router)
dp.include_router(admin_actions.router)

async def main() -> None:
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
