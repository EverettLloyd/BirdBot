import logging
from aiogram import Bot
from aiogram.types import InputMediaPhoto
from aiogram.exceptions import TelegramBadRequest
from config import settings

logger = logging.getLogger(__name__)

FORM_TITLES = {
    "owner": "📤 <b>Анкета владельца птицы</b>",
    "seeker": "📥 <b>Анкета соискателя</b>",
    "lost":   "🆘 <b>Потерялась птица</b>",
    "found":  "✅ <b>Нашлась птица</b>",
}

FORM_TEMPLATES = {
    "owner": [
        ("city", "Город"),
        ("species", "Вид"),
        ("reason", "Причины"),
        ("health_info", "Обследования"),
        ("wishes", "Пожелания к новому дому"),
    ],
    "seeker": [
        ("city", "Город"),
        ("age", "Возраст"),
        ("occupation", "Работаете/учитесь"),
        ("housing", "Жильё"),
        ("pets_children", "Другие животные/дети до 7"),
        ("other_birds", "Птицы/обследования/врач/затраты"),
        ("experience", "Опыт (2–3 предложения)"),
        ("post_link", "Ссылка на пост"),
    ],
    "lost": [
        ("city", "Город"),
        ("species", "Вид"),
        ("datetime_lost", "Дата и время потери"),
        ("address", "Адрес"),
    ],
    "found": [
        ("city", "Город"),
        ("species", "Вид"),
        ("datetime_found", "Дата и время находки"),
        ("address", "Адрес"),
        ("help_care", "Нужна передержка"),
    ],
}

def _format_caption(form_type: str, data: dict, include_contacts: bool = False) -> str:
    """Форматирует анкету. Если include_contacts=False, контакты не включаются."""
    caption = [FORM_TITLES.get(form_type, f"<b>{form_type}</b>")]
    for key, label in FORM_TEMPLATES.get(form_type, []):
        value = data.get(key)
        if value is not None and str(value).strip():
            caption.append(f"{label}: {value}")
    if include_contacts:
        phone = data.get("phone")
        contact = data.get("contact")
        if phone:   caption.append(f"Телефон: {phone}")
        if contact: caption.append(f"Контакт в Telegram: {contact}")
    return "\n".join(caption)

def _format_contacts(data: dict) -> str:
    """Форматирует сообщение с контактами."""
    contacts = ["<b>📞 Контакты:</b>"]
    phone = data.get("phone")
    contact = data.get("contact")
    if phone:
        contacts.append(f"Телефон: {phone}")
    if contact:
        contacts.append(f"Контакт в Telegram: {contact}")
    return "\n".join(contacts) if len(contacts) > 1 else ""

async def _send_album_or_text(bot: Bot, chat_id: int, photos: list[str], caption: str, message_thread_id: int | None = None):
    """Отправляет альбом или текст. При ошибке топика отправляет в обычный чат."""
    error_messages = ("TOPIC_CLOSED", "MESSAGE_THREAD_NOT_FOUND", "TOPIC_DELETED")
    
    try:
        if not photos:
            await bot.send_message(chat_id, caption, parse_mode="HTML", message_thread_id=message_thread_id)
        elif len(photos) == 1:
            await bot.send_photo(chat_id, photos[0], caption=caption, parse_mode="HTML", message_thread_id=message_thread_id)
        else:
            media = [InputMediaPhoto(media=photos[0], caption=caption, parse_mode="HTML")]
            media += [InputMediaPhoto(media=p) for p in photos[1:]]
            await bot.send_media_group(chat_id, media, message_thread_id=message_thread_id)
        
        if message_thread_id:
            logger.info(f"Сообщение успешно отправлено в топик {message_thread_id}")
    except TelegramBadRequest as e:
        error_str = str(e)
        if any(err_msg in error_str for err_msg in error_messages):
            # Если топик недоступен (закрыт, удален или не найден), отправляем в обычный чат
            logger.warning(f"Топик недоступен ({error_str}), отправка в обычный чат")
            if not photos:
                await bot.send_message(chat_id, caption, parse_mode="HTML")
            elif len(photos) == 1:
                await bot.send_photo(chat_id, photos[0], caption=caption, parse_mode="HTML")
            else:
                media = [InputMediaPhoto(media=photos[0], caption=caption, parse_mode="HTML")]
                media += [InputMediaPhoto(media=p) for p in photos[1:]]
                await bot.send_media_group(chat_id, media)
        else:
            logger.error(f"Ошибка при отправке сообщения: {e}")
            raise

async def send_application_to_admin(
    data: dict, bot: Bot, *, form_type: str, photos_key: str = "photos"
):
    """Отправляет анкету администратору. Поддерживает отправку в топик форума."""
    # Формируем анкету без контактов
    caption = _format_caption(form_type, data, include_contacts=False)
    photos = data.get(photos_key, []) or []
    
    # Получаем ID топика из настроек
    topic_id = getattr(settings, "ADMIN_TOPIC_ID", None)
    
    if topic_id:
        logger.info(f"Отправка анкеты типа '{form_type}' в топик {topic_id}")
    else:
        logger.info(f"Отправка анкеты типа '{form_type}' в обычный чат (топик не указан)")
    
    # Отправляем анкету (без контактов)
    await _send_album_or_text(bot, settings.ADMIN_CHAT_ID, photos, caption, message_thread_id=topic_id)
    
    # Отправляем контакты отдельным сообщением
    contacts_text = _format_contacts(data)
    if contacts_text:
        error_messages = ("TOPIC_CLOSED", "MESSAGE_THREAD_NOT_FOUND", "TOPIC_DELETED")
        try:
            await bot.send_message(settings.ADMIN_CHAT_ID, contacts_text, parse_mode="HTML", message_thread_id=topic_id)
            if topic_id:
                logger.info(f"Контакты отправлены в топик {topic_id}")
        except TelegramBadRequest as e:
            error_str = str(e)
            if any(err_msg in error_str for err_msg in error_messages):
                # Если топик недоступен, отправляем в обычный чат
                logger.warning(f"Топик недоступен для контактов ({error_str}), отправка в обычный чат")
                await bot.send_message(settings.ADMIN_CHAT_ID, contacts_text, parse_mode="HTML")
            else:
                logger.error(f"Ошибка при отправке контактов: {e}")
                raise
