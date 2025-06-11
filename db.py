from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from models import Seeker, Owner
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from config import settings

router = Router()

# Настройка базы данных
DATABASE_URL = settings.DATABASE_URL
engine = create_async_engine(DATABASE_URL, echo=False)
async_session_factory = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session():
    async with async_session_factory() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Owner.metadata.create_all)
        await conn.run_sync(Seeker.metadata.create_all)

class SeekerForm(StatesGroup):
    age = State()
    city = State()
    housing = State()
    other_birds = State()
    animals_kids = State()
    experience = State()
    photos = State()

class OwnerForm(StatesGroup):
    species = State()
    city = State()
    age = State()
    gender = State()
    description = State()
    photos = State()
    contact = State()

@router.message(Command("Хочу приютить"))
async def start_seeker(message: types.Message, state: FSMContext):
    await state.set_state(SeekerForm.age)
    await message.answer("Укажите ваш возраст:")

@router.message(StateFilter(SeekerForm.age))
async def seeker_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(SeekerForm.city)
    await message.answer("Ваш город:")

@router.message(StateFilter(SeekerForm.city))
async def seeker_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(SeekerForm.housing)
    await message.answer("Своя или арендованная жилплощадь:")

@router.message(StateFilter(SeekerForm.housing))
async def seeker_housing(message: types.Message, state: FSMContext):
    await state.update_data(housing=message.text)
    await state.set_state(SeekerForm.other_birds)
    await message.answer("Есть ли другие птицы? Обследованы ли они:")

@router.message(StateFilter(SeekerForm.other_birds))
async def seeker_other_birds(message: types.Message, state: FSMContext):
    await state.update_data(other_birds=message.text)
    await state.set_state(SeekerForm.animals_kids)
    await message.answer("Другие животные или дети до 7 лет:")

@router.message(StateFilter(SeekerForm.animals_kids))
async def seeker_animals(message: types.Message, state: FSMContext):
    await state.update_data(animals_kids=message.text)
    await state.set_state(SeekerForm.experience)
    await message.answer("Опыт содержания птиц:")

@router.message(StateFilter(SeekerForm.experience))
async def seeker_experience(message: types.Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await state.set_state(SeekerForm.photos)
    kb = ReplyKeyboardBuilder()
    kb.button(text="Готово")
    await message.answer("Прикрепите до 5 фотографий. Отправьте 'Готово' когда закончите", reply_markup=kb.as_markup(resize_keyboard=True))

@router.message(StateFilter(SeekerForm.photos))
async def seeker_photos(message: types.Message, state: FSMContext):
    if not message.photo:
        return
    data = await state.get_data()
    photos = data.get("photos", [])
    if len(photos) >= 5:
        await message.answer("Достаточно фотографий. Отправьте 'Готово'.")
        return
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    await message.answer(f"Фото {len(photos)} получено")

@router.message(StateFilter(SeekerForm.photos), lambda m: m.text == "Готово")
async def seeker_photos_done(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])

    new_seeker = Seeker(
        age=data.get("age"),
        city=data.get("city"),
        housing=data.get("housing"),
        other_birds=data.get("other_birds"),
        animals_kids=data.get("animals_kids"),
        experience=data.get("experience"),
        photo_ids=",".join(photos)
    )

    async for session in get_session():
        session.add(new_seeker)
        await session.commit()

    await message.answer("Спасибо, ваша заявка отправлена администратору.")
    await state.clear()

@router.message(Command("Отдать птицу"))
async def start_owner(message: types.Message, state: FSMContext):
    await state.set_state(OwnerForm.species)
    await message.answer("Укажите вид птицы:")

@router.message(StateFilter(OwnerForm.species))
async def owner_species(message: types.Message, state: FSMContext):
    await state.update_data(species=message.text)
    await state.set_state(OwnerForm.city)
    await message.answer("Город:")

@router.message(StateFilter(OwnerForm.city))
async def owner_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await state.set_state(OwnerForm.age)
    await message.answer("Возраст птицы:")

@router.message(StateFilter(OwnerForm.age))
async def owner_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(OwnerForm.gender)
    await message.answer("Пол птицы:")

@router.message(StateFilter(OwnerForm.gender))
async def owner_gender(message: types.Message, state: FSMContext):
    await state.update_data(gender=message.text)
    await state.set_state(OwnerForm.description)
    await message.answer("Краткое описание:")

@router.message(StateFilter(OwnerForm.description))
async def owner_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(OwnerForm.photos)
    kb = ReplyKeyboardBuilder()
    kb.button(text="Готово")
    await message.answer("Прикрепите до 5 фото. Отправьте 'Готово' по завершении", reply_markup=kb.as_markup(resize_keyboard=True))

@router.message(StateFilter(OwnerForm.photos))
async def owner_photos(message: types.Message, state: FSMContext):
    if not message.photo:
        return
    data = await state.get_data()
    photos = data.get("photos", [])
    if len(photos) >= 5:
        await message.answer("Достаточно фотографий. Отправьте 'Готово'.")
        return
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    await message.answer(f"Фото {len(photos)} получено")

@router.message(StateFilter(OwnerForm.photos), lambda m: m.text == "Готово")
async def owner_photos_done(message: types.Message, state: FSMContext):
    await state.set_state(OwnerForm.contact)
    await message.answer("Оставьте способ связи:", reply_markup=types.ReplyKeyboardRemove())

@router.message(StateFilter(OwnerForm.contact))
async def owner_contact(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])

    new_owner = Owner(
        species=data.get("species"),
        city=data.get("city"),
        age=data.get("age"),
        gender=data.get("gender"),
        description=data.get("description"),
        contact=message.text,
        photo_ids=",".join(photos)
    )

    async for session in get_session():
        session.add(new_owner)
        await session.commit()

    await message.answer("Заявка отправлена администраторам.")
    await state.clear()
