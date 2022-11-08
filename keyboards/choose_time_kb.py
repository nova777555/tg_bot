from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from data_base import db_scripts
import emoji
import datetime

def make_keyBoard(id,date):
    kb = InlineKeyboardMarkup(row_width = 2)
    now = datetime.datetime.now()
    H = now.strftime('%H')
    M = now.strftime('%M')
    t = int(H)*2+int(M)/30.0
    times = db_scripts.get_times(id,date,t)
    for time in times:
        h = int(time[0]) // 2
        m = (int(time[0]) % 2) * 30
        if m == 0: m = '00'
        kb.insert(InlineKeyboardButton(text = f"{h}:{m}", 
        callback_data = f'choose_time_{id}_{date}_{time[0]}'))
    kb.row(InlineKeyboardButton('Назад ' + emoji.emojize(":arrow_heading_up:", language='alias'),callback_data = f'back_{id}'))
    return kb
