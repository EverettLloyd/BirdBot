# keyboards.py
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton

BTN_OWNER  = "🔄 Отдать птицу"
BTN_SEEKER = "🐣 Хочу приютить"
BTN_LOST   = "🆘 Потерялась птица"
BTN_FOUND  = "✅ Нашлась птица"
BTN_CANCEL = "❌ Отмена"
BTN_SKIP   = "⏭ Пропустить"


def main_menu_kb():
    kb = ReplyKeyboardBuilder()
    for text in (BTN_OWNER, BTN_SEEKER, BTN_LOST, BTN_FOUND):
        kb.button(text=text)
    kb.adjust(2, 2)
    return kb.as_markup(resize_keyboard=True)

def done_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Готово")
    kb.button(text=BTN_CANCEL)
    kb.adjust(2, 1)
    return kb.as_markup(resize_keyboard=True)

def phone_kb():
    kb = ReplyKeyboardBuilder()
    kb.add(KeyboardButton(text="📱 Поделиться номером", request_contact=True))
    kb.button(text=BTN_CANCEL)
    kb.adjust(2, 1)
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)

def cancel_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text=BTN_CANCEL)
    return kb.as_markup(resize_keyboard=True, one_time_keyboard=True)

def yes_no_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Да")
    kb.button(text="Нет")
    kb.button(text=BTN_CANCEL)
    kb.adjust(2, 1)
    return kb.as_markup(resize_keyboard=True)

def skip_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text=BTN_SKIP)
    kb.button(text=BTN_CANCEL)
    kb.adjust(2, 1)
    return kb.as_markup(resize_keyboard=True)