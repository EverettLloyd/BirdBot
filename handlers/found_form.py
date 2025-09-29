from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards import main_menu_kb, yes_no_kb, BTN_CANCEL
from photos import ask_photos as ask_photos_step, setup_photos_step
from phone import ask_phone, setup_phone_step
from config import settings
from finalizer import finalize_form

router = Router()

class FoundForm(StatesGroup):
    city = State()
    species = State()
    datetime_found = State()
    address = State()
    help_care = State()
    photos = State()
    phone = State()

async def start_found(message: Message, state: FSMContext):
    await message.answer("Город:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(FoundForm.city)

@router.message(lambda m: m.text == BTN_CANCEL)
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Анкета прервана.", reply_markup=main_menu_kb())

@router.message(FoundForm.city)
async def ask_species(message: Message, state: FSMContext):
    await state.update_data(city=(message.text or "").strip())
    await message.answer("Вид птицы (если не уверены — опишите):")
    await state.set_state(FoundForm.species)

@router.message(FoundForm.species)
async def ask_datetime(message: Message, state: FSMContext):
    await state.update_data(species=(message.text or "").strip())
    await message.answer("Дата и время находки:")
    await state.set_state(FoundForm.datetime_found)

@router.message(FoundForm.datetime_found)
async def ask_address(message: Message, state: FSMContext):
    await state.update_data(datetime_found=(message.text or "").strip())
    await message.answer("Адрес (район, ориентиры):")
    await state.set_state(FoundForm.address)

@router.message(FoundForm.address)
async def ask_help_care(message: Message, state: FSMContext):
    await state.update_data(address=(message.text or "").strip())
    await message.answer("Нужна ли бесплатная профессиональная передержка у одного из админов?", reply_markup=yes_no_kb())
    await state.set_state(FoundForm.help_care)

@router.message(FoundForm.help_care, F.text.in_(["Да", "Нет"]))
async def handle_help_care(message: Message, state: FSMContext):
    answer = message.text
    await state.update_data(help_care=answer)
    if answer == "Да" and getattr(settings, "CARE_ADMIN_CONTACT", None):
        await message.answer(f"Свяжитесь с администратором: {settings.CARE_ADMIN_CONTACT}")
    # переходим к фото
    await ask_photos_step(message, state, max_photos=5)
    await state.set_state(FoundForm.photos)

# если вместо Да/Нет ввели что-то иное
@router.message(FoundForm.help_care)
async def handle_wrong_help_care(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, выберите вариант: Да / Нет.", reply_markup=yes_no_kb())

async def proceed_to_phone(message: Message, state: FSMContext):
    await ask_phone(message, state)
    await state.set_state(FoundForm.phone)

setup_photos_step(router, FoundForm.photos, on_done=proceed_to_phone, photos_key="photos", max_photos=5)

async def finalize_found(message: Message, state: FSMContext):
    await finalize_form(message, state, form_type="found")

setup_phone_step(router, FoundForm.phone, finalize_found)
