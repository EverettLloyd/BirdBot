from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext

from handlers.seeker_form import start_seeker
from handlers.owner_form import start_owner

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    kb = ReplyKeyboardBuilder()
    kb.button(text="🐣 Хочу приютить")
    kb.button(text="🔄 Отдать птицу")
    kb.adjust(1, 1)
    await message.answer("Выберите действие:", reply_markup=kb.as_markup(resize_keyboard=True))

@router.message(lambda m: m.text == "🐣 Хочу приютить")
async def handle_seeker_button(message: types.Message, state: FSMContext):
    await start_seeker(message, state)


@router.message(lambda m: m.text == ("🔄 Отдать птицу"))
async def handle_owner_button(message: types.Message, state: FSMContext):
    await start_owner(message, state)
