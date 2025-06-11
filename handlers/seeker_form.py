from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from messaging import send_application_to_admin

router = Router()

class SeekerForm(StatesGroup):
    age = State()
    city = State()
    housing = State()
    other_birds = State()
    pets_children = State()
    experience = State()
    photos = State()

@router.message(F.text == "Заполнить анкету")
async def start_seeker(message: Message, state: FSMContext):
    await message.answer("1. Укажите ваш возраст:")
    await state.set_state(SeekerForm.age)

@router.message(SeekerForm.age)
async def ask_city(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("2. Укажите город проживания:")
    await state.set_state(SeekerForm.city)

@router.message(SeekerForm.city)
async def ask_housing(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("3. Проживаете в своей или арендованной квартире?")
    await state.set_state(SeekerForm.housing)

@router.message(SeekerForm.housing)
async def ask_other_birds(message: Message, state: FSMContext):
    await state.update_data(housing=message.text)
    await message.answer("4. Есть ли другие птицы? Были ли они обследованы?")
    await state.set_state(SeekerForm.other_birds)

@router.message(SeekerForm.other_birds)
async def ask_pets(message: Message, state: FSMContext):
    await state.update_data(other_birds=message.text)
    await message.answer("5. Есть ли другие животные или дети до 7 лет?")
    await state.set_state(SeekerForm.pets_children)

@router.message(SeekerForm.pets_children)
async def ask_experience(message: Message, state: FSMContext):
    await state.update_data(pets_children=message.text)
    await message.answer("6. Расскажите об опыте содержания птиц:")
    await state.set_state(SeekerForm.experience)

@router.message(SeekerForm.experience)
async def ask_photos(message: Message, state: FSMContext):
    await state.update_data(experience=message.text)
    await message.answer(
        "7. Пришлите фотографии условий, в которых будет содержаться птица.\n"
        "Когда отправите все фото, нажмите кнопку \"Готово\".",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Готово")]],
            resize_keyboard=True,
        ),
    )
    await state.set_state(SeekerForm.photos)

@router.message(SeekerForm.photos, F.photo)
async def handle_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)

@router.message(SeekerForm.photos, F.text == "Готово")
async def handle_done(message: Message, state: FSMContext):
    data = await state.get_data()
    # Добавляем username как контакт
    contact = message.from_user.username or f"id:{message.from_user.id}"
    data["contact"] = f"@{contact}" if message.from_user.username else contact
    await send_application_to_admin(data, message.bot)
    await message.answer(
        "Заявка отправлена, спасибо, с вами свяжется администратор.",
        reply_markup=ReplyKeyboardMarkup(keyboard=[[]], resize_keyboard=True),
    )
    await state.clear()
