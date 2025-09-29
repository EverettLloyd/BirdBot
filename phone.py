# phone.py
import re
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards import phone_kb

PHONE_RE = re.compile(r"^\+\d{10,15}$")

def normalize_phone(raw: str) -> str:
    """Нормализуем телефон: очищаем, добавляем '+' для ведущей 7."""
    s = re.sub(r"[^\d+]", "", raw or "")
    if s.startswith("7") and not s.startswith("+"):
        s = f"+{s}"
    return s

def phone_prompt_text() -> str:
    return "Укажите номер телефона для связи. Можно нажать кнопку для отправки или введите вручную."

async def ask_phone(message: Message, state: FSMContext):
    """Показываем шаг ввода телефона (текст + клавиатура)."""
    await message.answer(phone_prompt_text(), reply_markup=phone_kb())
    # состояние устанавливает вызывающая сторона

def setup_phone_step(router: Router, phone_state, on_done):
    """
    Регистрирует 2 хэндлера для шага ввода телефона:
    - contact (кнопка 'Поделиться номером')
    - text (ручной ввод)

    on_done: async def on_done(message: Message, state: FSMContext) -> None
    Должен завершать форму (или делать следующее действие).
    """

    @router.message(phone_state, F.contact)
    async def _got_contact(message: Message, state: FSMContext):
        phone = normalize_phone(getattr(message.contact, "phone_number", ""))
        if not PHONE_RE.match(phone):
            await message.answer("Номер от Telegram выглядит странно. Введите вручную в формате +71234567890.")
            return
        await state.update_data(phone=phone)
        await on_done(message, state)

    @router.message(phone_state)
    async def _got_text(message: Message, state: FSMContext):
        phone = normalize_phone(message.text or "")
        if not PHONE_RE.match(phone):
            await message.answer("Кажется, номер в неверном формате. Пример: +71234567890. Попробуйте ещё раз.")
            return
        await state.update_data(phone=phone)
        await on_done(message, state)
