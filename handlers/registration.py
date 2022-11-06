#Обработка регистрации
from aiogram import types, Dispatcher
from create_bot import bot, dp
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from data_bases.db_scripts import add_user
from keyboards import kb_reg, kb_main_menu
from aiogram.types import ReplyKeyboardRemove
from data_bases import db_scripts
from handlers import main_h

#Класс состояний - последовательность регистрации
class FSMregistration(StatesGroup):
    name = State()
    surname = State()
    snils = State()
    number = State()

#Начало регистрации - приветствие
async def command_start(message : types.Message):
    await FSMregistration.name.set()
    await bot.send_message(message.from_user.id,'Мы рады приветствовать вас в нашем боте! \n Для доступа к функционалу необходима регистрация')
    await bot.send_message(message.from_user.id,'Введите, пожалуйста, ваше имя:')

#Получаем имя
async def take_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMregistration.next()
    await bot.send_message(message.from_user.id,'Введите фамилию:')

#Получаем фамилию
async def take_surname(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['surname'] = message.text
    await FSMregistration.next()
    await bot.send_message(message.from_user.id,'Введите номер СНИЛСа:')

#Получаем номер СНИЛСа
async def take_snils(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['snils'] = message.text
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
        await bot.send_message(message.from_user.id,'Успешное завершение, благодарим за регистрацию!',reply_markup = kb_main_menu)
        await main_h.FSMmain.main_menu.set()

#Регистрация обработчиков (хендлеров)
def register_handlers_registration(dp : Dispatcher):
    dp.register_message_handler(command_start, commands = ['start'], state = None)
    dp.register_message_handler(take_name, state = FSMregistration.name)
    dp.register_message_handler(take_surname, state = FSMregistration.surname)
    dp.register_message_handler(take_snils, state = FSMregistration.snils)
    dp.register_message_handler(take_phone_number,content_types =['contact'], state = FSMregistration.number)