from aiogram import Router, types
from aiogram.filters import CallbackQuery
from config import settings

router = Router()

@router.callback_query()
async def process_admin_action(query: types.CallbackQuery) -> None:
    if query.data == "approve":
        await query.message.answer("Заявка одобрена")
    elif query.data == "decline":
        await query.message.answer("Заявка отклонена")
    await query.answer()

