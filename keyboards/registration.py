from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

b = KeyboardButton('Поделиться контактом', request_contact = True)

kb_reg = ReplyKeyboardMarkup(resize_keyboard = True)

kb_reg.add(b)

b1 = KeyboardButton('Мужской')
b2 = KeyboardButton('Женский')

kb_choose_sex = ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard = True)

kb_choose_sex.add(b1).add(b2)