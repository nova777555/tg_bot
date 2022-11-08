from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import emoji

kb_confirm = ReplyKeyboardMarkup(resize_keyboard = True, one_time_keyboard = True)

b1 = KeyboardButton('Все верно ' + emoji.emojize(":white_check_mark:", language='alias'))
b2 = KeyboardButton('Назад' + emoji.emojize(":arrow_left:", language='alias'))

kb_confirm.add(b1).add(b2)