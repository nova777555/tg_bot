from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from data_base import db_scripts
import emoji

def make_keyBoard(id,page):
    kb = InlineKeyboardMarkup(row_width = 2)
    days = db_scripts.get_days(id,page)
    for day in days:
        kb.insert(InlineKeyboardButton(text = f"{day[0].split('-')[2]}.{day[0].split('-')[1]}({day[1]})", 
        callback_data = f'choose_day_{day[0]}_{id}'))
    kb.row(InlineKeyboardButton('Записаться на ближайшее время', callback_data = f'choose_nearest_{id}'))
    kb.row(InlineKeyboardButton('Предыдущая ' + emoji.emojize(":arrow_left:", language='alias'),callback_data = f'page_{page-1}_{id}'),
    InlineKeyboardButton('Назад ' + emoji.emojize(":arrow_heading_up:", language='alias'),callback_data = 'back'),
    InlineKeyboardButton('Следующая ' + emoji.emojize(":arrow_right:", language='alias'),callback_data = f'page_{page+1}_{id}'))  
    return kb
