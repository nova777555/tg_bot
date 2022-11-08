from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import emoji
from data_base import db_scripts

def make_kb_option(id):
    kb = ReplyKeyboardMarkup(resize_keyboard = True)
    if (int(*db_scripts.get_notification_status(id)[0]) == 1):
        b = KeyboardButton('Отключить уведомления ' + emoji.emojize(":mute:", language='alias'))
    else:
        b = KeyboardButton('Включить уведомления ' + emoji.emojize(":sound:", language='alias'))
    kb.add(b)
    kb.add(KeyboardButton('Назад ' + emoji.emojize(":arrow_left:", language='alias')))
    return kb