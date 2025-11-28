from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards import main_menu_kb, BTN_CANCEL, cancel_kb
from phone import ask_phone, setup_phone_step
from photos import ask_photos as ask_photos_step, setup_photos_step
from finalizer import finalize_form

router = Router()

class LostForm(StatesGroup):
    city = State()
    species = State()
    datetime_lost = State()
    address = State()
    photos = State() 
    phone = State()

async def start_lost(message: Message, state: FSMContext):
    await message.answer("Город:", reply_markup=cancel_kb())
    await state.set_state(LostForm.city)

@router.message(F.text == BTN_CANCEL)
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Анкета прервана.", reply_markup=main_menu_kb())

@router.message(LostForm.city)
async def ask_species(message: Message, state: FSMContext):
    await state.update_data(city=(message.text or "").strip())
    await message.answer("Вид птицы:", reply_markup=cancel_kb())
    await state.set_state(LostForm.species)

@router.message(LostForm.species)
async def ask_datetime(message: Message, state: FSMContext):
    await state.update_data(species=(message.text or "").strip())
    await message.answer("Дата и время потери:", reply_markup=cancel_kb())
    await state.set_state(LostForm.datetime_lost)

@router.message(LostForm.datetime_lost)
async def ask_address(message: Message, state: FSMContext):
    await state.update_data(datetime_lost=(message.text or "").strip())
    await message.answer(
        "Адрес (район, ориентиры):", reply_markup=cancel_kb()
    )
    await state.set_state(LostForm.address)

@router.message(LostForm.address)
async def ask_photos(message: Message, state: FSMContext):
    await state.update_data(address=(message.text or "").strip())
    await ask_photos_step(message, state, max_photos=5)
    await state.set_state(LostForm.photos)

async def proceed_to_phone(message: Message, state: FSMContext):
    await ask_phone(message, state)
    await state.set_state(LostForm.phone)

setup_photos_step(router, LostForm.photos, on_done=proceed_to_phone, photos_key="photos", max_photos=5)


async def finalize_lost(message: Message, state: FSMContext):
    await finalize_form(message, state, form_type="lost")

setup_phone_step(router, LostForm.phone, finalize_lost)
