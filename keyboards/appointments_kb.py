from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import emoji

kb_appointment = ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard = True)

b1 = KeyboardButton('Назад' + emoji.emojize(":arrow_left:", language='alias'))

kb_appointment.add(b1)