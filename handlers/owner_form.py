from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards import main_menu_kb, BTN_CANCEL, cancel_kb
from photos import ask_photos as ask_photos_step, setup_photos_step
from phone import ask_phone, setup_phone_step
from finalizer import finalize_form

router = Router()

class OwnerForm(StatesGroup):
    city = State()
    species = State()
    reason = State()
    health_info = State()
    photos = State()
    wishes = State()
    phone = State()

async def start_owner(message: Message, state: FSMContext):
    await message.answer("Укажите город:", reply_markup=cancel_kb())
    await state.set_state(OwnerForm.city)

@router.message(F.text == BTN_CANCEL)
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Анкета прервана.", reply_markup=main_menu_kb())

@router.message(OwnerForm.city)
async def ask_species(message: Message, state: FSMContext):
    await state.update_data(city=(message.text or "").strip())
    await message.answer("Вид птицы:", reply_markup=cancel_kb())
    await state.set_state(OwnerForm.species)

@router.message(OwnerForm.species)
async def ask_reason(message: Message, state: FSMContext):
    await state.update_data(species=(message.text or "").strip())
    await message.answer("Причина пристройства:", reply_markup=cancel_kb())
    await state.set_state(OwnerForm.reason)

@router.message(OwnerForm.reason)
async def ask_health(message: Message, state: FSMContext):
    await state.update_data(reason=(message.text or "").strip())
    await message.answer("Посещала ли птица врача? Если да, то ФИО врача, результаты обследований:", reply_markup=cancel_kb())
    await state.set_state(OwnerForm.health_info)

@router.message(OwnerForm.health_info)
async def ask_photos(message: Message, state: FSMContext):
    await state.update_data(health_info=(message.text or "").strip())
    await ask_photos_step(message, state, max_photos=5)
    await state.set_state(OwnerForm.photos)

async def proceed_to_wishes(message: Message, state: FSMContext):
    await message.answer("Укажите ваши пожелания к новому дому: поддерживать обратную связь в виде фото и видео, продолжить обращаться к тому же лечащему врачу и тд:", reply_markup=cancel_kb())
    await state.set_state(OwnerForm.wishes)

setup_photos_step(router, OwnerForm.photos, on_done=proceed_to_wishes, photos_key="photos", max_photos=5)

@router.message(OwnerForm.wishes)
async def ask_phone_step(message: Message, state: FSMContext):
    await state.update_data(wishes=(message.text or "").strip())
    await ask_phone(message, state)
    await state.set_state(OwnerForm.phone)

async def finalize_owner(message: Message, state: FSMContext):
    await finalize_form(message, state, form_type="owner")

setup_phone_step(router, OwnerForm.phone, finalize_owner)
