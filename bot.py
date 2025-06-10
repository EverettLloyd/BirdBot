import json
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

# States for first form
FORM1_NAME, FORM1_AGE, FORM1_PHOTO = range(3)
# States for second form
FORM2_TEXT, FORM2_PHOTO = range(3, 5)

def store_form(form_type: str, data: dict) -> None:
    record = {"type": form_type, **data}
    try:
        with open("forms.json", "r", encoding="utf-8") as f:
            records = json.load(f)
    except FileNotFoundError:
        records = []
    records.append(record)
    with open("forms.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Выберите анкету: /form1 или /form2. Отправьте /cancel для отмены."
    )
    return ConversationHandler.END

# --- Form 1 handlers ---
async def form1_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите ваше имя:")
    return FORM1_NAME

async def form1_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Введите ваш возраст:")
    return FORM1_AGE

async def form1_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["age"] = update.message.text
    await update.message.reply_text("Прикрепите фотографию:")
    return FORM1_PHOTO

async def form1_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photo = update.message.photo[-1]
    context.user_data["photo_file_id"] = photo.file_id
    store_form("form1", context.user_data)
    context.user_data.clear()
    await update.message.reply_text("Спасибо! Анкета 1 получена.")
    return ConversationHandler.END

# --- Form 2 handlers ---
async def form2_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите текст отзыва:")
    return FORM2_TEXT

async def form2_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["text"] = update.message.text
    await update.message.reply_text("Прикрепите фотографию:")
    return FORM2_PHOTO

async def form2_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    photo = update.message.photo[-1]
    context.user_data["photo_file_id"] = photo.file_id
    store_form("form2", context.user_data)
    context.user_data.clear()
    await update.message.reply_text("Спасибо! Анкета 2 получена.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END

def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("Set BOT_TOKEN environment variable")
    application = Application.builder().token(token).build()

    form1_conv = ConversationHandler(
        entry_points=[CommandHandler("form1", form1_start)],
        states={
            FORM1_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, form1_name)],
            FORM1_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, form1_age)],
            FORM1_PHOTO: [MessageHandler(filters.PHOTO, form1_photo)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    form2_conv = ConversationHandler(
        entry_points=[CommandHandler("form2", form2_start)],
        states={
            FORM2_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, form2_text)],
            FORM2_PHOTO: [MessageHandler(filters.PHOTO, form2_photo)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(form1_conv)
    application.add_handler(form2_conv)

    application.run_polling()

if __name__ == "__main__":
    main()
