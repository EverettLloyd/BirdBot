from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards import main_menu_kb, BTN_CANCEL
from messaging import send_application_to_admin
from photos import ask_photos as ask_photos_step, setup_photos_step
from phone import ask_phone, setup_phone_step

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
    await message.answer("Укажите город:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(OwnerForm.city)

@router.message(lambda m: m.text == BTN_CANCEL)
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Анкета прервана.", reply_markup=main_menu_kb())

@router.message(OwnerForm.city)
async def ask_species(message: Message, state: FSMContext):
    await state.update_data(city=(message.text or "").strip())
    await message.answer("Вид птицы:")
    await state.set_state(OwnerForm.species)

@router.message(OwnerForm.species)
async def ask_reason(message: Message, state: FSMContext):
    await state.update_data(species=(message.text or "").strip())
    await message.answer("Причина пристройства:")
    await state.set_state(OwnerForm.reason)

@router.message(OwnerForm.reason)
async def ask_health(message: Message, state: FSMContext):
    await state.update_data(reason=(message.text or "").strip())
    await message.answer("Обследования и анализы:")
    await state.set_state(OwnerForm.health_info)

@router.message(OwnerForm.health_info)
async def ask_photos(message: Message, state: FSMContext):
    await state.update_data(health_info=(message.text or "").strip())
    await ask_photos_step(message, state, max_photos=5)
    await state.set_state(OwnerForm.photos)

async def proceed_to_wishes(message: Message, state: FSMContext):
    await message.answer("Пожелания к новому дому (врач, держать связь и т.д.):")
    await state.set_state(OwnerForm.wishes)

setup_photos_step(router, OwnerForm.photos, on_done=proceed_to_wishes, photos_key="photos", max_photos=5)

@router.message(OwnerForm.wishes)
async def ask_phone_step(message: Message, state: FSMContext):
    await state.update_data(wishes=(message.text or "").strip())
    await ask_phone(message, state)
    await state.set_state(OwnerForm.phone)

async def finalize_owner(message: Message, state: FSMContext):
    data = await state.get_data()
    tg = message.from_user.username or f"id:{message.from_user.id}"
    data["contact"] = f"@{tg}" if message.from_user.username else tg
    await send_application_to_admin(data, message.bot, form_type="owner")
    await message.answer("Анкета отправлена. С вами свяжется администратор.", reply_markup=main_menu_kb())
    await state.clear()

setup_phone_step(router, OwnerForm.phone, finalize_owner)
