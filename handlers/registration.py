#Обработка регистрации
from aiogram import types, Dispatcher
from create_bot import bot, dp
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards import kb_reg, kb_main_menu, kb_main_menu_admin, kb_choose_sex
from aiogram.types import ReplyKeyboardRemove, KeyboardButton
from data_base import db_scripts
from handlers import main_h
import emoji
import re

#Класс состояний - последовательность регистрации
class FSMregistration(StatesGroup):
    name = State()
    surname = State()
    sex = State()
    birthday = State()
    snils = State()
    number = State()

#Начало регистрации - приветствие
async def command_start(message : types.Message):
    if len(db_scripts.find_user(message.from_user.id)) == 1:
        await main_h.FSMmain.main_menu.set()
        if str(message.from_user.id) in [str(a[0]) for a in list(db_scripts.get_doctors_id())]:
            await bot.send_message(message.from_user.id, 'Что умеет давнный бот? \n По первой кнопке вы можете записаться к врачу в удобный для вас день и подходящее время. \n При этом, если вы не значете, к какому специалисту обратиться - бот сможет вам помочь: достаточно будет выбрать соответствующую кнопку и перечислить свои жалобы \n \n Также по кнопке \'Мои записи\' вы сможете ознакомиться с вашими совершенными записями, по кнопке \'Связь с дежурным врачом\' вы сможете получить его контакт и позвонить в случае необходимости \n Также вы можете не пользоваться кнопками и написать ваш запрос вручную боту, находясь в главном меню, например \'Запишите меня к терапевту на ближайшее время\''
            ,reply_markup = kb_main_menu_admin)
        else:
            await bot.send_message(message.from_user.id, 'Что умеет давнный бот? \n По первой кнопке вы можете записаться к врачу в удобный для вас день и подходящее время. \n При этом, если вы не значете, к какому специалисту обратиться - бот сможет вам помочь: достаточно будет выбрать соответствующую кнопку и перечислить свои жалобы \n \n Также по кнопке \'Мои записи\' вы сможете ознакомиться с вашими совершенными записями, по кнопке \'Связь с дежурным врачом\' вы сможете получить его контакт и позвонить в случае необходимости \n Также вы можете не пользоваться кнопками и написать ваш запрос вручную боту, находясь в главном меню, например \'Запишите меня к терапевту на ближайшее время\''
            ,reply_markup = kb_main_menu)
    else: 
        await FSMregistration.name.set()
        await bot.send_message(message.from_user.id,'Мы рады приветствовать вас в нашем боте! \n Для доступа к функционалу необходима регистрация')
        await bot.send_message(message.from_user.id,'Введите, пожалуйста, ваше имя:')

#Получаем имя
async def take_name(message: types.Message, state: FSMContext):
    if message.text == re.sub(r'[^\w\s]','', message.text): 
        async  with state.proxy() as data:
            data['name'] = message.text
        await FSMregistration.next()
        await bot.send_message(message.from_user.id,'Введите фамилию:')
    else:
        await bot.send_message(message.from_user.id,'Пожалуйста, проверьте правильность ввденный данных')

#Получаем фамилию
async def take_surname(message: types.Message, state: FSMContext):
    if message.text == re.sub(r'[^\w\s]','', message.text): 
        async with state.proxy() as data:
            data['surname'] = message.text
        await FSMregistration.next()
        await bot.send_message(message.from_user.id,'Выберите ваш пол:', reply_markup = kb_choose_sex)
    else:
        await bot.send_message(message.from_user.id,'Пожалуйста, проверьте правильность ввденный данных') 

#Получаем пол, 1=Мужской, 2=Женский
async def take_sex(message: types.Message, state: FSMContext):
    flag = False
    async with state.proxy() as data:
        if message.text == 'Мужской':
            data['sex'] = 1
            flag = True
        elif message.text == 'Женский':
            data['sex'] = 0
            flag = True
    if flag:
        await FSMregistration.next()
        await bot.send_message(message.from_user.id,'Введите дату рождения в формате DD.MM.YYYY:')

#Получаем дату рождения
async def take_birthday(message: types.Message, state: FSMContext):
    flag = False
    async with state.proxy() as data:
        d = message.text.split('.')
        data['birthday'] = f'{d[2]}-{d[1]}-{d[0]}'
        flag = True
    if flag:
        await FSMregistration.next()
        await bot.send_message(message.from_user.id,'Введите номер полиса:')

#Получаем номер полиса
async def take_polis(message: types.Message, state: FSMContext):
    flag = False
    async with state.proxy() as data:
        data['polis'] = message.text
        flag = True
    if flag:
        await FSMregistration.next()
        await bot.send_message(message.from_user.id,'Поделитесь контактом для завершения регистрации:',reply_markup = kb_reg)

#Получаем номер телефона и id пользователя
async def take_phone_number(message: types.Contact, state: FSMContext):
    if message.contact is not None:
        async with state.proxy() as data:
            data['number'] = str(message.contact.phone_number)
            data['id'] = str(message.contact.user_id)
        #Сохранение пользователя в БД
        await db_scripts.add_user(state)
        await state.finish()
        await main_h.FSMmain.main_menu.set()
        await bot.send_message(message.from_user.id,'Успешное завершение, благодарим за регистрацию!')
        if str(message.from_user.id) in [str(a[0]) for a in list(db_scripts.get_doctors_id())]:
            await bot.send_message(message.from_user.id, 'Что умеет давнный бот? \n По первой кнопке вы можете записаться к врачу в удобный для вас день и подходящее время. \n При этом, если вы не значете, к какому специалисту обратиться - бот сможет вам помочь: достаточно будет выбрать соответствующую кнопку и перечислить свои жалобы \n \n Также по кнопке \'Мои записи\' вы сможете ознакомиться с вашими совершенными записями, по кнопке \'Связь с дежурным врачом\' вы сможете получить его контакт и позвонить в случае необходимости \n Также вы можете не пользоваться кнопками и написать ваш запрос вручную боту, находясь в главном меню, например \'Запишите меня к терапевту на ближайшее время\''
            ,reply_markup = kb_main_menu_admin)
        else:
            await bot.send_message(message.from_user.id, 'Что умеет давнный бот? \n По первой кнопке вы можете записаться к врачу в удобный для вас день и подходящее время. \n При этом, если вы не значете, к какому специалисту обратиться - бот сможет вам помочь: достаточно будет выбрать соответствующую кнопку и перечислить свои жалобы \n \n Также по кнопке \'Мои записи\' вы сможете ознакомиться с вашими совершенными записями, по кнопке \'Связь с дежурным врачом\' вы сможете получить его контакт и позвонить в случае необходимости \n Также вы можете не пользоваться кнопками и написать ваш запрос вручную боту, находясь в главном меню, например \'Запишите меня к терапевту на ближайшее время\''
            ,reply_markup = kb_main_menu)

#Регистрация обработчиков (хендлеров)
def register_handlers_registration(dp : Dispatcher):
    dp.register_message_handler(command_start, commands = ['start'], state = None)
    dp.register_message_handler(take_name, state = FSMregistration.name)
    dp.register_message_handler(take_surname, state = FSMregistration.surname)
    dp.register_message_handler(take_polis, state = FSMregistration.snils)
    dp.register_message_handler(take_sex, state = FSMregistration.sex)
    dp.register_message_handler(take_birthday, state = FSMregistration.birthday)
    dp.register_message_handler(take_phone_number,content_types =['contact'], state = FSMregistration.number)