from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import emoji

kb_main_menu = ReplyKeyboardMarkup(resize_keyboard = True)

b1 = KeyboardButton('Записаться к врачу ' + emoji.emojize(":hospital:"))
b2 = KeyboardButton('Мои записи' + emoji.emojize(":memo:"))
b3 = KeyboardButton('Связь с дежурным врачом ' + emoji.emojize(":phone:", language='alias'))

kb_main_menu.add(b1).add(b2).add(b3)