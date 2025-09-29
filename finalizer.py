from typing import Optional
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards import main_menu_kb
from messaging import send_application_to_admin

# Глобальный текст по умолчанию (меняется один раз — применяется везде)
DEFAULT_FINAL_TEXT = (
    "Анкета отправлена. С вами свяжется администратор.\n"
    "Ваше объявление будет опубликовано в нашем канале "
    "https://t.me/parrotsmom_help"
)

# (Опционально) Персональные тексты для конкретных форм
# Если ключа нет — будет использован DEFAULT_FINAL_TEXT
FORM_FINAL_TEXT: dict[str, str] = {
    # "owner": "Спасибо! Мы свяжемся с вами по поводу пристройства.",
    # "seeker": "Спасибо! Мы свяжемся, как только подберём птицу.",
    # "lost":   "Заявка принята. Мы поможем с поиском.",
    # "found":  "Спасибо! Администратор свяжется по поводу найденной птицы.",
}

async def finalize_form(
    message: Message,
    state: FSMContext,
    *,
    form_type: str,
    duplicate_to_channel: bool = False,
    custom_text: Optional[str] = None,
) -> None:
    """
    Универсальная финализация: добавляет контакт, отправляет анкету админу/в канал,
    показывает главное меню и очищает FSM.

    - form_type: ключ шаблона в messaging.FORM_TEMPLATES / FORM_TITLES
    - duplicate_to_channel: при True дубль улетит в канал (если настроен)
    - custom_text: переопределяет текст финального сообщения (если нужно точечно)
    """
    data = await state.get_data()

    # Контакт Telegram (username или сырой id)
    tg = message.from_user.username or f"id:{message.from_user.id}"
    data["contact"] = f"@{tg}" if message.from_user.username else tg

    # Отправка анкеты
    await send_application_to_admin(
        data,
        message.bot,
        form_type=form_type,
        duplicate_to_channel=duplicate_to_channel,
    )

    # Текст финального сообщения
    text = (
        custom_text
        or FORM_FINAL_TEXT.get(form_type)
        or DEFAULT_FINAL_TEXT
    )

    # Ответ пользователю + возврат главного меню
    await message.answer(text, reply_markup=main_menu_kb())

    # Очистка состояния
    await state.clear()
