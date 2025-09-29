from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards import main_menu_kb, BTN_OWNER, BTN_SEEKER, BTN_LOST, BTN_FOUND
from handlers.owner_form import start_owner
from handlers.seeker_form import start_seeker
from handlers.lost_form import start_lost
from handlers.found_form import start_found

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Выберите действие:", reply_markup=main_menu_kb())

@router.message(lambda m: m.text == BTN_OWNER)
async def go_owner(message: types.Message, state: FSMContext):
    await start_owner(message, state)

@router.message(lambda m: m.text == BTN_SEEKER)
async def go_seeker(message: types.Message, state: FSMContext):
    await start_seeker(message, state)

@router.message(lambda m: m.text == BTN_LOST)
async def go_lost(message: types.Message, state: FSMContext):
    await start_lost(message, state)

@router.message(lambda m: m.text == BTN_FOUND)
async def go_found(message: types.Message, state: FSMContext):
    await start_found(message, state)
