from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

b = KeyboardButton('Поделиться контактом', request_contact = True)

kb_reg = ReplyKeyboardMarkup(resize_keyboard = True)

kb_reg.add(b)