from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import emoji

kb_new_appointment1 = ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard = True)

b1 = KeyboardButton('Я знаю к кому записаться ' + emoji.emojize(":white_check_mark:", language='alias'))
b2 = KeyboardButton('Мне нужна помощь с выбором врача' + emoji.emojize(":question:", language='alias'))
b3 = KeyboardButton('Назад ' + emoji.emojize(":arrow_left:", language='alias'))

kb_new_appointment1.add(b1).add(b2).add(b3)