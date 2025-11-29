from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards import done_kb, BTN_CANCEL, main_menu_kb

DEFAULT_MAX_PHOTOS = 5

def photos_prompt_text(max_photos: int = DEFAULT_MAX_PHOTOS) -> str:
    return (
        f"Пришлите до {max_photos} фотографий. "
        "Когда отправите все фото, нажмите «Готово»."
    )

async def ask_photos(message: Message, state: FSMContext, *, max_photos: int = DEFAULT_MAX_PHOTOS, custom_prompt_text: str = None):
    """Показываем шаг с фотографиями (текст + клавиатура «Готово»)."""
    prompt = custom_prompt_text if custom_prompt_text else photos_prompt_text(max_photos)
    await message.answer(prompt, reply_markup=done_kb())
    # состояние устанавливает вызывающая сторона

def setup_photos_step(
    router: Router,
    photos_state,
    on_done,
    *,
    photos_key: str = "photos",
    max_photos: int = DEFAULT_MAX_PHOTOS,
    ack_each_photo: bool = False,
):
    """
    Регистрирует 2 хэндлера для шага добавления фото:
    - F.photo: копим file_id до max_photos
    - F.text == "Готово": вызываем on_done(message, state)

    on_done: async def on_done(message: Message, state: FSMContext) -> None
    photos_key: ключ в FSM-состоянии, куда складывать список фото
    ack_each_photo: если True — подтверждаем приём каждого фото сообщением
    """

    @router.message(photos_state, F.photo)
    async def _got_photo(message: Message, state: FSMContext):
        data = await state.get_data()
        photos = list(data.get(photos_key, []))
        if len(photos) >= max_photos:
            await message.answer("Достаточно фотографий. Нажмите «Готово».")
            return
        photos.append(message.photo[-1].file_id)
        await state.update_data(**{photos_key: photos})
        if ack_each_photo:
            await message.answer(f"Фото {len(photos)} получено.")

    @router.message(photos_state, F.text == "Готово")
    async def _done(message: Message, state: FSMContext):
        await on_done(message, state)

    @router.message(photos_state, F.text == BTN_CANCEL)
    async def _cancel(message: Message, state: FSMContext):
        await state.clear()
        await message.answer("Анкета прервана.", reply_markup=main_menu_kb())
