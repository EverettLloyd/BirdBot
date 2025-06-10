from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    kb = ReplyKeyboardBuilder()
hnfqpb-codex/создать-телеграм-бота-для-анкет-с-фото
    kb.button(text="🐣 Хочу приютить")
    kb.button(text="🔄 Отдать птицу")
main
    kb.adjust(1, 1)
    await message.answer(
        "Выберите действие:", reply_markup=kb.as_markup(resize_keyboard=True)
    )
