from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards import main_menu_kb, BTN_CANCEL
from photos import ask_photos as ask_photos_step, setup_photos_step
from phone import ask_phone, setup_phone_step
from finalizer import finalize_form

router = Router()

class SeekerForm(StatesGroup):
    city = State()
    age = State()
    occupation = State()
    housing = State()
    pets_children = State()
    other_birds = State()
    experience = State()
    photos = State()
    phone = State()

async def start_seeker(message: Message, state: FSMContext):
    await message.answer("Укажите город:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(SeekerForm.city)

@router.message(lambda m: m.text == BTN_CANCEL)
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Анкета прервана.", reply_markup=main_menu_kb())

@router.message(SeekerForm.city)
async def ask_age(message: Message, state: FSMContext):
    await state.update_data(city=(message.text or "").strip())
    await message.answer("Ваш возраст:")
    await state.set_state(SeekerForm.age)

@router.message(SeekerForm.age)
async def ask_occupation(message: Message, state: FSMContext):
    await state.update_data(age=(message.text or "").strip())
    await message.answer("Вы работаете, учитесь?")
    await state.set_state(SeekerForm.occupation)

@router.message(SeekerForm.occupation)
async def ask_housing(message: Message, state: FSMContext):
    await state.update_data(occupation=(message.text or "").strip())
    await message.answer("Жильё: своё или аренда?")
    await state.set_state(SeekerForm.housing)

@router.message(SeekerForm.housing)
async def ask_pets_children(message: Message, state: FSMContext):
    await state.update_data(housing=(message.text or "").strip())
    await message.answer("Другие животные в доме, дети до 7 лет:")
    await state.set_state(SeekerForm.pets_children)

@router.message(SeekerForm.pets_children)
async def ask_other_birds(message: Message, state: FSMContext):
    await state.update_data(pets_children=(message.text or "").strip())
    await message.answer("Если есть птицы: обследования? к какому врачу ходите? готовы к затратам?")
    await state.set_state(SeekerForm.other_birds)

@router.message(SeekerForm.other_birds)
async def ask_experience(message: Message, state: FSMContext):
    await state.update_data(other_birds=(message.text or "").strip())
    await message.answer("В 2–3 предложениях об опыте содержания: что знаете, чем кормите:")
    await state.set_state(SeekerForm.experience)

@router.message(SeekerForm.experience)
async def ask_photos(message: Message, state: FSMContext):
    await state.update_data(experience=(message.text or "").strip())
    await ask_photos_step(message, state, max_photos=5)
    await state.set_state(SeekerForm.photos)

async def proceed_to_phone(message: Message, state: FSMContext):
    await ask_phone(message, state)
    await state.set_state(SeekerForm.phone)

setup_photos_step(router, SeekerForm.photos, on_done=proceed_to_phone, photos_key="photos", max_photos=5)

async def finalize_seeker(message: Message, state: FSMContext):
    await finalize_form(message, state, form_type="seeker")

setup_phone_step(router, SeekerForm.phone, finalize_seeker)
