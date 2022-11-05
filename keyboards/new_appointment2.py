from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from data_bases import db_scripts
import emoji

kb_new_appointment2 = InlineKeyboardMarkup()

i = 0
for doctor in db_scripts.get_doctors():
    kb_new_appointment2.add(InlineKeyboardButton(text = doctor[0] + ' (' + doctor[1] + ')', callback_data = 'doctor_'+str(i)+'_new'))
    i+=1
kb_new_appointment2.add(InlineKeyboardButton('Назад ' + emoji.emojize(":arrow_left:", language='alias'),callback_data = 'back'))
