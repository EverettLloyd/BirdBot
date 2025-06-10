from aiogram import Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from database.models import SeekerApplication, Photo
from database.session import async_session
from config import settings

router = Router()

class SeekerForm(StatesGroup):
    age = State()
    city = State()
    housing = State()
    other_birds = State()
    animals_kids = State()
    experience = State()
    photos = State()

@router.message(Command("Хочу приютить"))
async def start_seeker(message: types.Message, state: FSMContext) -> None:
    await state.set_state(SeekerForm.age)
    await message.answer("Укажите ваш возраст:")

@router.message(StateFilter(SeekerForm.age))
async def seeker_age(message: types.Message, state: FSMContext) -> None:
    await state.update_data(age=message.text)
    await state.set_state(SeekerForm.city)
    await message.answer("Ваш город:")

@router.message(StateFilter(SeekerForm.city))
async def seeker_city(message: types.Message, state: FSMContext) -> None:
    await state.update_data(city=message.text)
    await state.set_state(SeekerForm.housing)
    await message.answer("Своя или арендованная жилплощадь:")

@router.message(StateFilter(SeekerForm.housing))
async def seeker_housing(message: types.Message, state: FSMContext) -> None:
    await state.update_data(housing=message.text)
    await state.set_state(SeekerForm.other_birds)
    await message.answer("Есть ли другие птицы? Обследованы ли они:")

@router.message(StateFilter(SeekerForm.other_birds))
async def seeker_other_birds(message: types.Message, state: FSMContext) -> None:
    await state.update_data(other_birds=message.text)
    await state.set_state(SeekerForm.animals_kids)
    await message.answer("Другие животные или дети до 7 лет:")

@router.message(StateFilter(SeekerForm.animals_kids))
async def seeker_animals(message: types.Message, state: FSMContext) -> None:
    await state.update_data(animals_kids=message.text)
    await state.set_state(SeekerForm.experience)
    await message.answer("Опыт содержания птиц:")

@router.message(StateFilter(SeekerForm.experience))
async def seeker_experience(message: types.Message, state: FSMContext) -> None:
    await state.update_data(experience=message.text)
    await state.set_state(SeekerForm.photos)
    kb = ReplyKeyboardBuilder()
    kb.button(text="Готово")
    await message.answer(
        "Прикрепите до 5 фотографий. Отправьте 'Готово' когда закончите",
        reply_markup=kb.as_markup(resize_keyboard=True),
    )

@router.message(StateFilter(SeekerForm.photos), Command("Готово"))
@router.message(StateFilter(SeekerForm.photos), lambda m: m.text == "Готово")
async def seeker_photos_done(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    app = SeekerApplication(
        user_id=message.from_user.id,
        age=data.get("age"),
        city=data.get("city"),
        housing=data.get("housing"),
        other_birds=data.get("other_birds"),
        animals_kids=data.get("animals_kids"),
        experience=data.get("experience"),
    )
    async with async_session() as session:
        session.add(app)
        await session.commit()
    photos = data.get("photos", [])
    admin_text = (
        f"Возраст: {data.get('age')}\n"
        f"Город: {data.get('city')}\n"
        f"Жильё: {data.get('housing')}\n"
        f"Другие птицы: {data.get('other_birds')}\n"
        f"Животные/дети: {data.get('animals_kids')}\n"
        f"Опыт: {data.get('experience')}"
    )

    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text="Одобрить", callback_data="approve"),
                types.InlineKeyboardButton(text="Отклонить", callback_data="decline"),
            ]
        ]
    )

    if photos:
        first, *rest = photos
        await message.bot.send_photo(
            settings.ADMIN_CHAT_ID,
            first,
            caption=admin_text,
            reply_markup=kb,
        )
        for photo in rest:
            await message.bot.send_photo(settings.ADMIN_CHAT_ID, photo)
    else:
        await message.bot.send_message(
            settings.ADMIN_CHAT_ID,
            admin_text,
            reply_markup=kb,
        )

    await message.answer(
        "Спасибо, ваша заявка отправлена администратору.",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await state.clear()

@router.message(StateFilter(SeekerForm.photos), content_types=types.ContentType.PHOTO)
async def seeker_photos(message: types.Message, state: FSMContext) -> None:
    data = await state.get_data()
    photos = data.get("photos", [])
    if len(photos) >= 5:
        await message.answer("Достаточно фотографий. Отправьте 'Готово'.")
        return
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    await message.answer(f"Фото {len(photos)} получено")

