from aiogram import Router, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from messaging import send_application_to_admin

router = Router()

class OwnerForm(StatesGroup):
    bird_name = State()
    bird_type = State()
    health_info = State()
    reason = State()
    wishes = State()
    photos = State()

@router.message(F.text == "Пристроить птицу")
async def start_owner(message: Message, state: FSMContext):
    await message.answer("1. Укажите имя птицы:")
    await state.set_state(OwnerForm.bird_name)

@router.message(OwnerForm.bird_name)
async def ask_type(message: Message, state: FSMContext):
    await state.update_data(bird_name=message.text)
    await message.answer("2. Вид, пол, возраст птицы:")
    await state.set_state(OwnerForm.bird_type)

@router.message(OwnerForm.bird_type)
async def ask_health(message: Message, state: FSMContext):
    await state.update_data(bird_type=message.text)
    await message.answer("3. Состояние здоровья, наличие анализов:")
    await state.set_state(OwnerForm.health_info)

@router.message(OwnerForm.health_info)
async def ask_reason(message: Message, state: FSMContext):
    await state.update_data(health_info=message.text)
    await message.answer("4. Причина пристройства:")
    await state.set_state(OwnerForm.reason)

@router.message(OwnerForm.reason)
async def ask_wishes(message: Message, state: FSMContext):
    await state.update_data(reason=message.text)
    await message.answer("5. Пожелания к будущим хозяевам:")
    await state.set_state(OwnerForm.wishes)

@router.message(OwnerForm.wishes)
async def ask_photos(message: Message, state: FSMContext):
    await state.update_data(wishes=message.text)
    await message.answer(
        "6. Пришлите фотографии птицы.\nКогда отправите все фото, нажмите кнопку \"Готово\".",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Готово")]],
            resize_keyboard=True,
        ),
    )
    await state.set_state(OwnerForm.photos)

@router.message(OwnerForm.photos, F.photo)
async def handle_photo(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)

@router.message(OwnerForm.photos, F.text == "Готово")
async def handle_done(message: Message, state: FSMContext):
    data = await state.get_data()
    contact = message.from_user.username or f"id:{message.from_user.id}"
    data["contact"] = f"@{contact}" if message.from_user.username else contact
    await send_application_to_admin(data, message.bot, is_owner=True)
    await message.answer(
        "Анкета отправлена. С вами свяжется администратор.",
        reply_markup=ReplyKeyboardMarkup(keyboard=[[]], resize_keyboard=True),
    )
    await state.clear()
