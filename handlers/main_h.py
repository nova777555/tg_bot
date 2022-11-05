from aiogram import types, Dispatcher
from create_bot import bot, dp
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from data_bases import db_scripts
from aiogram.dispatcher.filters import Text
import emoji
from keyboards import kb_main_menu, kb_new_appointment1, kb_new_appointment2
from aiogram.dispatcher.filters.state import State, StatesGroup

#Класс состояний - для сохранения введенных симптомов или команд
class FSMmain(StatesGroup):
    main_menu = State()
    new_appointment = State()
    choose_doctor_by_yourself = State()
    symptoms = State()
    command = State()

#Новая запись к врачу, переход к выбору: самостоятельно или через распознование симптомов
async def new_appointment(message: types.Message):
    await FSMmain.new_appointment.set()
    await bot.send_message(message.from_user.id, text = 'Выберите', reply_markup = kb_new_appointment1)

#Выбор доктора самостоятельно
async def choose_doctor_byyourself(message: types.Message):
    await FSMmain.choose_doctor_by_yourself.set()
    await bot.send_message(message.from_user.id, text = 'Выберите', reply_markup = kb_new_appointment2)

#Назад к варинтам выбора доктора
async def back_to_new_appointment(callback: types.CallbackQuery):
    await FSMmain.new_appointment.set()
    await callback.message.answer('Выберете', reply_markup = kb_new_appointment1)
    await callback.answer()

#Назад в главное меню
async def back_to_main_menu(message: types.Message):
    await FSMmain.main_menu.set()
    await bot.send_message(message.from_user.id, text = 'Главное меню', reply_markup = kb_main_menu)

#Регистрация хендлеров
def register_handlers_menu(dp : Dispatcher):
    dp.register_message_handler(back_to_main_menu, commands = ['menu'])
    dp.register_message_handler(new_appointment, lambda message: message.text == 'Записаться к врачу ' + emoji.emojize(":hospital:"), state = FSMmain.main_menu)
    dp.register_message_handler(back_to_main_menu, lambda message: message.text == 'Назад ' + emoji.emojize(":arrow_left:", language='alias'), state = FSMmain.new_appointment)
    dp.register_callback_query_handler(back_to_new_appointment, text = 'back', state = FSMmain.choose_doctor_by_yourself)
    dp.register_message_handler(choose_doctor_byyourself, lambda message: message.text == 'Я знаю к кому записаться ' + emoji.emojize(":white_check_mark:", language='alias'), state = FSMmain.new_appointment)

