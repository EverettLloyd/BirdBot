import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import settings
from handlers import main_menu, seeker_form, owner_form, lost_form, found_form


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()


dp.include_router(main_menu.router)
dp.include_router(owner_form.router)
dp.include_router(seeker_form.router)
dp.include_router(lost_form.router)
dp.include_router(found_form.router)


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())