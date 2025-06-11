from aiogram import Bot
from config import settings


async def send_application_to_admin(data: dict, bot: Bot, is_owner: bool = False):
    caption_lines = []

    if is_owner:
        caption_lines.append("📤 <b>Анкета владельца птицы</b>")
        caption_lines.append(f"🐦 Имя птицы: {data.get('bird_name')}")
        caption_lines.append(f"📋 Вид, пол, возраст: {data.get('bird_type')}")
        caption_lines.append(f"🩺 Здоровье и анализы: {data.get('health_info')}")
        caption_lines.append(f"❓ Причина пристройства: {data.get('reason')}")
        caption_lines.append(f"🎯 Пожелания к хозяевам: {data.get('wishes')}")
    else:
        caption_lines.append("📥 <b>Анкета соискателя</b>")
        caption_lines.append(f"🎂 Возраст: {data.get('age')}")
        caption_lines.append(f"📍 Город: {data.get('city')}")
        caption_lines.append(f"🏠 Жильё: {data.get('housing')}")
        caption_lines.append(f"🕊️ Другие птицы: {data.get('other_birds')}")
        caption_lines.append(f"👶 Дети/Животные: {data.get('pets_children')}")
        caption_lines.append(f"🧠 Опыт: {data.get('experience')}")

    caption_lines.append(f"📱 Контакт: {data.get('contact')}")

    caption = "\n".join(caption_lines)
    photos = data.get("photos", [])

    if photos:
        # Отправляем первое фото с подписью
        await bot.send_photo(
            chat_id=settings.ADMIN_CHAT_ID,
            photo=photos[0],
            caption=caption,
            parse_mode="HTML"
        )

        # Остальные фото — без подписи
        for photo_id in photos[1:]:
            await bot.send_photo(chat_id=settings.ADMIN_CHAT_ID, photo=photo_id)
    else:
        # Если фото нет, просто отправим текст
        await bot.send_message(chat_id=settings.ADMIN_CHAT_ID, text=caption, parse_mode="HTML")
