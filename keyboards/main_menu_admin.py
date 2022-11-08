from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import emoji

kb_main_menu_admin = ReplyKeyboardMarkup(resize_keyboard = True)

b1 = KeyboardButton('Записаться к врачу ' + emoji.emojize(":hospital:"))
b2 = KeyboardButton('Мои записи' + emoji.emojize(":memo:"))
b3 = KeyboardButton('Связь с дежурным врачом ' + emoji.emojize(":phone:", language='alias'))
b4 = KeyboardButton('Настройки ' + emoji.emojize(":wrench:", language='alias'))
b5 = KeyboardButton('Моё расписание')

kb_main_menu_admin.add(b1).add(b2).add(b3).add(b4).add(b5)