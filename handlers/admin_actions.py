from aiogram import Router, types
from aiogram.types import CallbackQuery
from config import settings

router = Router()

@router.callback_query()
async def process_admin_action(query: types.CallbackQuery) -> None:
    if query.message.chat.id != settings.ADMIN_CHAT_ID:
        await query.answer()
        return
    if query.data == "approve":
        await query.message.answer("Заявка одобрена")
    elif query.data == "decline":
        await query.message.answer("Заявка отклонена")
    await query.answer()

