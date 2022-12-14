from aiogram import types, Dispatcher
from create_bot import bot, dp
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from data_base import db_scripts
from aiogram.dispatcher.filters import Text
import emoji
from aiogram.types import  InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton
from keyboards import kb_main_menu, kb_new_appointment1, kb_new_appointment2, choose_day_kb, choose_time_kb, confirm, appointments_kb
from keyboards.options import make_kb_option
from keyboards.main_menu_admin import kb_main_menu_admin
from aiogram.dispatcher.filters.state import State, StatesGroup
import datetime
from data_base.excel import Export


#Количество страниц с выбором дней
MAX_PAGE = 3

#Класс состояний - для сохранения введенных симптомов или команд
class FSMmain(StatesGroup):
    main_menu = State()
    confirm = State()
    new_appointment = State()
    choose_doctor_by_yourself = State()
    choose_doctor_by_bot = State()
    choose_day = State()
    choose_time = State()
    symptoms = State()
    my_appointments = State()
    options = State()
    sos = State()

def time_to_h_m(time):
    h = int(time) // 2
    m = (int(time) % 2) * 30
    if m == 0: m = '00'
    return (h,m)

#Новая запись к врачу, переход к выбору: самостоятельно или через распознование симптомов
async def new_appointment(message: types.Message):
    await message.delete()
    await FSMmain.new_appointment.set()
    await bot.send_message(message.from_user.id, text = 'Как вам удобнее подобрать специалиста?', reply_markup = kb_new_appointment1)

#Список совершенных записей
async def my_appointments(message: types.Message):
    await FSMmain.my_appointments.set()
    await bot.send_message(message.from_user.id, text = 'Ваши записи:', reply_markup = appointments_kb.kb_appointment)
    now = datetime.datetime.now()
    H = now.strftime('%H')
    M = now.strftime('%M')
    t = int(H)*2+int(M)/30.0
    date = '\''+now.strftime('%Y')+'-'+now.strftime('%m')+'-'+now.strftime('%d')+'\''
    appointments = db_scripts.get_appointments(message.from_user.id,t,date)
    for app in appointments:
        data = list(*db_scripts.get_info_appointment(app[0]))
        doctor = list(*db_scripts.get_info_doctor(data[2]))
        date = data[0].split('-')
        time = data[1]
        h,m = time_to_h_m(time)
        await bot.send_message(message.from_user.id, text = f'Запись на прием к {doctor[0]} ({doctor[1]}), {date[2]}.{date[1]} в {h}:{m}', reply_markup = InlineKeyboardMarkup().add(InlineKeyboardButton('Отменить ' + emoji.emojize(":no_entry_sign:", language='alias'),callback_data = f'cancel_{app[0]}')))

#Отмена записи
async def cancel_appointment(callback: types.CallbackQuery):
    await callback.message.delete()
    await db_scripts.cancel_appointment(int(callback.data.split('_')[1]))
    await callback.message.answer('Запись успешно отменена')
    await callback.answer()

#Выбор доктора самостоятельно
async def choose_doctor_byyourself(message: types.Message):
    await FSMmain.choose_doctor_by_yourself.set()
    await bot.send_message(message.from_user.id, text = 'Выберете нужного врача', reply_markup = kb_new_appointment2)

#Оформление записи на выбранное время, возврат в главное меню
async def succes_confirm(message: types.Message, state: FSMContext):
    await FSMmain.main_menu.set()
    await db_scripts.make_appointment(state, message.from_user.id)
    if str(message.from_user.id) in [str(a[0]) for a in list(db_scripts.get_doctors_id())]:
        await bot.send_message(message.from_user.id, text = 'Окно закрплено за вами! \n Все свои записи можно найти в главном меню', reply_markup = kb_main_menu_admin)
    else:
        await bot.send_message(message.from_user.id, text = 'Окно закрплено за вами! \n Все свои записи можно найти в главном меню', reply_markup = kb_main_menu)

#Оформление записи на ближайшее время, подтверждение выданного окна
async def choose_nearest(callback: types.CallbackQuery, state: FSMContext):
    await FSMmain.confirm.set()
    now = datetime.datetime.now()
    H = now.strftime('%H')
    M = now.strftime('%M')
    t = int(H)*2+int(M)/30.0
    doctor = list(*db_scripts.get_info_doctor(callback.data.split('_')[2]))
    async with state.proxy() as data:
        data['date'] = list(db_scripts.get_days(callback.data.split('_')[2],1,t))[0][0]
        date = data['date'].split('-')
        data['time'] = list(db_scripts.get_times(callback.data.split('_')[2],data['date'],t))[0][0]
        data['id'] = callback.data.split('_')[2]
        time = data['time']
        h,m = time_to_h_m(time)
    await callback.message.delete()
    await callback.message.answer(f'Подтвердите запись: \n Запись на прием к {doctor[0]} ({doctor[1]}), {date[2]}.{date[1]} в {h}:{m}', reply_markup = confirm.kb_confirm)
    await callback.answer()

#Назад к варинтам выбора доктора
async def back_to_new_appointment(callback: types.CallbackQuery):
    await FSMmain.new_appointment.set()
    await callback.message.delete()
    await callback.message.answer('Как вам удобнее подобрать специалиста?', reply_markup = kb_new_appointment1)
    await callback.answer()

#Назад к варинтам выбора доктора
async def back_to_new_appointment_bt(message: types.Message):
    await FSMmain.new_appointment.set()
    await message.delete()
    await message.answer('Как вам удобнее подобрать специалиста?', reply_markup = kb_new_appointment1)

#Назад к списку докторов
async def back_to_choose_doctor_by_youself(callback: types.CallbackQuery):
    await FSMmain.choose_doctor_by_yourself.set()
    await callback.message.delete()
    await callback.message.answer('Выберите нужного врача', reply_markup = kb_new_appointment2)
    await callback.answer()

#Назад к списку дней
async def back_to_choose_day(callback: types.CallbackQuery):
    await FSMmain.choose_day.set()
    await callback.message.delete()
    await callback.message.answer(f'Выберите удобный день для посещения (Страница 1 из {MAX_PAGE})', reply_markup = choose_day_kb.make_keyBoard(int(callback.data.split('_')[1]),1))
    await callback.answer()

#Назад к списку окон
async def back_to_choose_time(message: types.Message, state: FSMContext):
    await FSMmain.choose_time.set()
    async with state.proxy() as data:
        await bot.send_message(message.from_user.id, text = 'Выберите удобное время для посещения ' + data['date'].split('-')[2] + '.' + data['date'].split('-')[1],
         reply_markup = choose_time_kb.make_keyBoard(data['id'],data['date']))

#Выбор дня посещения
async def choose_day(callback, state : FSMContext, s = 0):
    tg_id = 0
    flag = False
    async with state.proxy() as data:
        tg_id = data['user_id']
    if s == 0:
        flag = True
        s = callback.data
        await callback.message.delete()
    await FSMmain.choose_day.set()
    page = 1
    await bot.send_message(tg_id, text = f'Выберите удобный день для посещения (Страница {page} из {MAX_PAGE})', reply_markup = choose_day_kb.make_keyBoard(int(s.split('_')[2]),page))
    if flag:
        await callback.answer()

#Выбор времени посещения
async def choose_time(callback, state : FSMContext, s=0):
    flag = False
    if s == 0:
        await callback.message.delete()
        s = callback.data
        flag = True
    tg_id = 0
    async with state.proxy() as data:
        tg_id = data['user_id']
    await FSMmain.choose_time.set()
    await bot.send_message(tg_id, text = 'Выберете удобное время для посещения ' + s.split('_')[2].split('-')[2]+'.'+s.split('_')[2].split('-')[1],
     reply_markup = choose_time_kb.make_keyBoard(s.split('_')[3],s.split('_')[2]))
    if flag:
        await callback.answer()

#Подтверждение записи
async def confirm_appointment(callback, state: FSMContext, s = 0):
    await FSMmain.confirm.set()
    flag = False
    if s == 0:
        flag = True
        await callback.message.delete()
        s = callback.data
    doctor = list(*db_scripts.get_info_doctor(s.split('_')[2]))
    date = s.split('_')[3].split('-')
    time = s.split('_')[4]
    h,m = time_to_h_m(time)
    tg_id = 0
    async with state.proxy() as data:
        data['id'] = s.split('_')[2]
        data['date'] = s.split('_')[3]
        data['time'] = s.split('_')[4]
        tg_id = data['user_id']
    await bot.send_message(tg_id, text = f'Подтвердите запись: \n Запись на прием к {doctor[0]} ({doctor[1]}), {date[2]}.{date[1]} в {h}:{m}', reply_markup = confirm.kb_confirm)
    if flag:
        await callback.answer()

#Смена страницы дней посещения
async def change_page_choosing_day(callback: types.CallbackQuery):
    await FSMmain.choose_day.set()
    page = int(callback.data.split('_')[1])
    await callback.message.delete()
    if page < 1 : page = 1
    if page > MAX_PAGE : page = MAX_PAGE
    await callback.message.answer(f'Выберете удобный день для посещения (Страница {page} из {MAX_PAGE})', reply_markup = choose_day_kb.make_keyBoard(int(callback.data.split('_')[2]),page))
    await callback.answer()

#Назад в главное меню
async def back_to_main_menu(message: types.Message, state: FSMContext):
    await FSMmain.main_menu.set()
    await message.delete()
    if str(message.from_user.id) in [str(a[0]) for a in list(db_scripts.get_doctors_id())]:
       await bot.send_message(message.from_user.id, text = 'Главное меню', reply_markup = kb_main_menu_admin)
    else:
        await bot.send_message(message.from_user.id, text = 'Главное меню', reply_markup = kb_main_menu)

#Настройки
async def options(message: types.Message):
    await FSMmain.options.set()
    await message.delete()
    await bot.send_message(message.from_user.id, text = 'Настройки', reply_markup = make_kb_option(message.from_user.id))

#Отключение уведомлений
async def notification_turn_off(message: types.Message):
    await db_scripts.update_notification(message.from_user.id,0)
    await FSMmain.main_menu.set()
    await message.delete()
    if str(message.from_user.id) in [str(a[0]) for a in list(db_scripts.get_doctors_id())]:
       await bot.send_message(message.from_user.id, text = 'Настройки обновлены', reply_markup = kb_main_menu_admin)
    else:
        await bot.send_message(message.from_user.id, text = 'НАстройки обновлены', reply_markup = kb_main_menu)

#Включение уведомлений
async def notification_turn_on(message: types.Message):
    await db_scripts.update_notification(message.from_user.id,1)
    await FSMmain.main_menu.set()
    await message.delete()
    if str(message.from_user.id) in [str(a[0]) for a in list(db_scripts.get_doctors_id())]:
       await bot.send_message(message.from_user.id, text = 'Настройки обновлены', reply_markup = kb_main_menu_admin)
    else:
        await bot.send_message(message.from_user.id, text = 'НАстройки обновлены', reply_markup = kb_main_menu)

#Получение расписания для врача
async def get_timetable(message: types.Message):
    await FSMmain.main_menu.set()
    path = "./bd.db"
    query_file_path = "./requests/first_request"
    excel_file_path = "./"
    exporter = Export(path)
    id = db_scripts.get_doctor_tgid(message.from_user.id)[0][0]
    exporter.excelFromQuery(id=id, query_from_file = True, 
                            query_file_path = query_file_path, 
                            excel_file_path = excel_file_path)
    await message.reply_document(open('./timetable.xlsx', 'rb'), reply_markup = kb_main_menu_admin)
    await message.delete()
#Связь с дежурным врачом
async def sos(message: types.Message):
    await FSMmain.sos.set()
    await message.delete()
    await bot.send_message(message.from_user.id, text = 'Информация для связи с врачом:', reply_markup = appointments_kb.kb_appointment)
    await bot.send_contact(message.from_user.id, '+79025102007', 'Горшокова', 'Ирина')

#Получение симптомов от пользователя, начало подбора доктора
async def choose_doctor_by_bot(message: types.Message, state:FSMContext):
    await FSMmain.symptoms.set()
    await message.delete()
    await bot.send_message(message.from_user.id, text = 'Введите, пожалуйста, через пробел ваши жалобы:', reply_markup = appointments_kb.kb_appointment)
    

#Регистрация хендлеров
def register_handlers_menu(dp : Dispatcher):
    dp.register_callback_query_handler(choose_day, Text(startswith = 'choose_doctor'), state = FSMmain.choose_doctor_by_yourself)
    dp.register_callback_query_handler(cancel_appointment, Text(startswith = 'cancel_'), state = FSMmain.my_appointments)
    dp.register_callback_query_handler(choose_time, Text(startswith = 'choose_day'), state = FSMmain.choose_day)
    dp.register_callback_query_handler(choose_nearest, Text(startswith = 'choose_nearest'), state = FSMmain.choose_day)
    dp.register_message_handler(new_appointment, lambda message: message.text == 'Записаться к врачу ' + emoji.emojize(":hospital:"), state = FSMmain.main_menu)
    dp.register_message_handler(my_appointments, lambda message: message.text == 'Мои записи' + emoji.emojize(":memo:"), state = FSMmain.main_menu)
    dp.register_message_handler(back_to_choose_time, lambda message: message.text == 'Назад' + emoji.emojize(":arrow_left:", language='alias'), state = FSMmain.confirm)
    dp.register_message_handler(back_to_main_menu, lambda message: message.text == 'Назад' + emoji.emojize(":arrow_left:", language='alias'), state = FSMmain.my_appointments)
    dp.register_message_handler(succes_confirm, lambda message: message.text == 'Все верно ' + emoji.emojize(":white_check_mark:", language='alias'), state = FSMmain.confirm)
    dp.register_message_handler(back_to_main_menu, lambda message: message.text == 'Назад ' + emoji.emojize(":arrow_left:", language='alias'), state = FSMmain.new_appointment)
    dp.register_message_handler(back_to_main_menu, lambda message: message.text == 'Назад ' + emoji.emojize(":arrow_left:", language='alias'), state = FSMmain.options)
    dp.register_callback_query_handler(back_to_new_appointment, text = 'back', state = FSMmain.choose_doctor_by_yourself)
    dp.register_callback_query_handler(back_to_choose_doctor_by_youself, text = 'back', state = FSMmain.choose_day)
    dp.register_callback_query_handler(back_to_choose_day, Text(startswith = 'back_'), state = FSMmain.choose_time)
    dp.register_callback_query_handler(confirm_appointment, Text(startswith = 'choose_time_'), state = FSMmain.choose_time)
    dp.register_callback_query_handler(change_page_choosing_day, Text(startswith = 'page_'), state = FSMmain.choose_day)
    dp.register_message_handler(choose_doctor_byyourself, lambda message: message.text == 'Я знаю к кому записаться ' + emoji.emojize(":white_check_mark:", language='alias'), state = FSMmain.new_appointment)
    dp.register_message_handler(choose_doctor_by_bot, lambda message: message.text == 'Мне нужна помощь с выбором врача' + emoji.emojize(":question:", language='alias'), state = FSMmain.new_appointment)
    dp.register_message_handler(options, lambda message: message.text == 'Настройки ' + emoji.emojize(":wrench:", language='alias'), state = FSMmain.main_menu)
    dp.register_message_handler(notification_turn_off, lambda message: message.text == 'Отключить уведомления ' + emoji.emojize(":mute:", language='alias'), state = FSMmain.options)
    dp.register_message_handler(notification_turn_on, lambda message: message.text == 'Включить уведомления ' + emoji.emojize(":sound:", language='alias'), state = FSMmain.options)
    dp.register_message_handler(get_timetable, lambda message: message.text == 'Моё расписание', state = FSMmain.main_menu)
    dp.register_message_handler(sos, lambda message: message.text == 'Связь с дежурным врачом ' + emoji.emojize(":phone:", language='alias'), state = FSMmain.main_menu)
    dp.register_message_handler(back_to_main_menu, lambda message: message.text == 'Назад' + emoji.emojize(":arrow_left:", language='alias'), state = FSMmain.sos)
    dp.register_message_handler(back_to_new_appointment_bt, lambda message: message.text == 'Назад' + emoji.emojize(":arrow_left:", language='alias'), state = FSMmain.symptoms)

