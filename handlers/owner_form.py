from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from database.models import OwnerApplication
from database.session import async_session

router = Router()

class OwnerForm(StatesGroup):
    species = State()
    city = State()
    age = State()
    gender = State()
    description = State()
    photos = State()
    contact = State()

@router.message(Command("Отдать птицу"))
async def start_owner(message: types.Message, state: FSMContext) -> None:
    await state.set_state(OwnerForm.species)
    await message.answer("Укажите вид птицы:")

@router.message(StateFilter(OwnerForm.species))
async def owner_species(message: types.Message, state: FSMContext) -> None:
    await state.update_data(species=message.text)
    await state.set_state(OwnerForm.city)
    await message.answer("Город:")

@router.message(StateFilter(OwnerForm.city))
async def owner_city(message: types.Message, state: FSMContext) -> None:
    await state.update_data(city=message.text)
    await state.set_state(OwnerForm.age)
    await message.answer("Возраст птицы:")

@router.message(StateFilter(OwnerForm.age))
async def owner_age(message: types.Message, state: FSMContext) -> None:
    await state.update_data(age=message.text)
    await state.set_state(OwnerForm.gender)
    await message.answer("Пол птицы:")

@router.message(StateFilter(OwnerForm.gender))
async def owner_gender(message: types.Message, state: FSMContext) -> None:
    await state.update_data(gender=message.text)
    await state.set_state(OwnerForm.description)
    await message.answer("Краткое описание:")

@router.message(StateFilter(OwnerForm.description))
async def owner_description(message: types.Message, state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await state.set_state(OwnerForm.photos)
    kb = ReplyKeyboardBuilder()
    kb.button(text="Готово")
    await message.answer(
        "Прикрепите до 5 фото. Отправьте 'Готово' по завершении",
        reply_markup=kb.as_markup(resize_keyboard=True),
    )

@router.message(StateFilter(OwnerForm.photos), Command("Готово"))
@router.message(StateFilter(OwnerForm.photos), lambda m: m.text == "Готово")
async def owner_photos_done(message: types.Message, state: FSMContext) -> None:
    await state.set_state(OwnerForm.contact)
    await message.answer("Оставьте способ связи:", reply_markup=types.ReplyKeyboardRemove())

@router.message(StateFilter(OwnerForm.photos), content_types=types.ContentType.PHOTO)
async def owner_photos(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    photos = data.get("photos", [])
    if len(photos) >= 5:
        await message.answer("Достаточно фотографий. Отправьте 'Готово'.")
        return
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    await message.answer(f"Фото {len(photos)} получено")

@router.message(StateFilter(OwnerForm.contact))
async def owner_contact(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    app = OwnerApplication(
        user_id=message.from_user.id,
        species=data.get("species"),
        city=data.get("city"),
        age=data.get("age"),
        gender=data.get("gender"),
        description=data.get("description"),
        contact=message.text,
    )
    async with async_session() as session:
        session.add(app)
        await session.commit()
    await message.answer("Заявка отправлена администраторам.")
    await state.clear()

