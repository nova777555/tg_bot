import re
from nltk.stem import SnowballStemmer
from spellchecker import SpellChecker
from nltk.tokenize import word_tokenize
import pymorphy2
from string import punctuation
from pymystem3 import Mystem
from nltk.corpus import stopwords
from aiogram import types, Dispatcher
from create_bot import bot, dp
from aiogram.dispatcher import FSMContext
from data_base import db_scripts
from aiogram.dispatcher.filters.state import State, StatesGroup
import datetime
from handlers.main_h import FSMmain, choose_day, choose_time, confirm_appointment, choose_doctor_by_bot, choose_day_kb
from keyboards import kb_main_menu, kb_main_menu_admin


# Create lemmatizer and stopwords list
russian_stopwords = stopwords.words("russian")
mystem = Mystem() 
spell = SpellChecker(language='ru')

def preprocess_text(text):
    tokens = mystem.lemmatize(text.lower())
    tokens = [ token for token in tokens if token not in russian_stopwords\
              and token != " " \
              and token.strip() not in punctuation]
    
    text = " ".join(tokens)
    text = word_tokenize(text)
    return text

def choose_doctor(simptomy):
    zapis = 0
    cardio = open('./data_base/cardio.txt', 'r', encoding="utf-8")
    gastro = open('./data_base/gastroenterologist.txt', 'r', encoding="utf-8")
    theraphist = open('./data_base/therapist.txt', 'r', encoding="utf-8")
    surgeon = open('./data_base/surgeon.txt', 'r', encoding="utf-8")
    spisok_simptomov_cardio = cardio.read().split(' ')
    spisok_simptomov_gastro = gastro.read().split(' ')
    spisok_simptomov_surgeon = surgeon.read().split(' ')
    spisok_simptomov_theraphist = theraphist.read().split(' ')
    simptomy = preprocess_text(simptomy)
    result_cardio = set(spisok_simptomov_cardio) & set(simptomy)
    result_surgeon = set(spisok_simptomov_surgeon) & set(simptomy)
    result_gastro = set(spisok_simptomov_gastro) & set(simptomy)
    result_therapist = set(spisok_simptomov_theraphist) & set(simptomy)
    if any([bool(set(result_cardio) & set(simptomy)) and bool(set(simptomy) & set(result_gastro)),
                bool(set(result_therapist) & set(simptomy)) and bool(set(result_cardio) & set(simptomy)),
                bool(set(result_surgeon) & set(simptomy)) and bool(set(result_cardio) & set(simptomy)),
                bool(set(result_therapist) & set(simptomy)) and bool(set(result_gastro) & set(simptomy)),
                bool(set(result_therapist) & set(simptomy)) and bool(set(result_surgeon) & set(simptomy)),
                bool(set(result_gastro) & set(simptomy)) and bool(set(result_surgeon) & set(simptomy))]
               ):
            zapis = 1
    elif result_cardio:
        zapis = 4
    elif result_gastro:
        zapis = 3
    elif result_surgeon:
        zapis = 2
    else:
        zapis = 1

    cardio.close()
    gastro.close()
    surgeon.close()
    theraphist.close()
    return zapis

def is_ok_date(date):
    today = datetime.date.today()
    date = [int(i) for i in date.split('-')]
    try:
        return datetime.date(*date) >= today 
    except: return False

def date_time_zapis(message):
    snowball = SnowballStemmer(language="russian")
    suggest = 0
    doc = -1
    correct = word_tokenize(message)
    correct = [snowball.stem(elem) for elem in correct]
    check_zapis = set(['запиш','записа','зап']) & set(correct)
    check_doctor = (set(['доктор']) & set(correct)) or (set(['врач']) & set(correct))
    if check_zapis:
        suggest = 1
        spisok_doctors = db_scripts.get_doctors()[:-2]
        for (index, elem) in enumerate(spisok_doctors):
            spisok_doctors[index] = [snowball.stem(el) for el in elem[0].split()]
            spisok_doctors[index].append(snowball.stem(elem[1]))
        therapist_name = spisok_doctors[0]
        surgeon_name = spisok_doctors[1]
        gastro_name = spisok_doctors[2]
        cardiolog_name = spisok_doctors[3]
        name_cardio = (set(cardiolog_name) & set(correct))
        name_gastro = set(gastro_name) & set(correct)
        name_surgeon = (set(surgeon_name) & set(correct))
        name_therapist = (set(therapist_name) & set(correct))
        if any([bool(set(cardiolog_name) & set(correct)) and bool(set(correct) & set(gastro_name)),
                bool(set(therapist_name) & set(correct)) and bool(set(cardiolog_name) & set(correct)),
                bool(set(surgeon_name) & set(correct)) and bool(set(cardiolog_name) & set(correct)),
                bool(set(therapist_name) & set(correct)) and bool(set(gastro_name) & set(correct)),
                bool(set(therapist_name) & set(correct)) and bool(set(surgeon_name) & set(correct)),
                bool(set(gastro_name) & set(correct)) and bool(set(cardiolog_name) & set(correct))]
               ):
            doc = 1
        elif name_cardio:
            doc = 4
        elif name_gastro:
            doc = 3
        elif name_surgeon:
            doc = 2
        elif name_therapist:
            doc = 1
        elif check_doctor:
            return [2]
        date = re.search(r'\d\d\.\d\d\.\d{4}',message) or re.search(r'\d\d\.\d\d',message)
        time = re.search(r'([01]?[0-9]|2[0-3]):([0-5][0-9])',message)
        if (not date) and (not time):
            return [1,f'choose_doctor_{doc}']
        if date:
            if not re.search(r'\d\d\.\d\d\.\d{4}',message):
                date = f"{date.group(0)}.{datetime.date.today().strftime('%Y')}"
            else:
                date = date.group(0)
            date = date.split('.')
            date = f'{date[2]}-{date[1]}-{date[0]}'
            if is_ok_date(date):
                return [3,f'choose_day_{date}_{doc}']
            else: 
                return [3,None]
    return 0


# Получение текстового запроса пользователя
async def get_command(message: types.Message, state : FSMContext):
    command = date_time_zapis(message.text)
    if command == 0:
        if str(message.from_user.id) in [str(a[0]) for a in list(db_scripts.get_doctors_id())]:
            await bot.send_message(message.from_user.id, text = 'Извините, не удалось распознать команду :с', reply_markup = kb_main_menu_admin)
        else:
            await bot.send_message(message.from_user.id, text = 'Извините, не удалось распознать команду :с', reply_markup = kb_main_menu)
    elif command[0] == 1:
        if command[1].split('_')[-1] == "-1": 
            c = command[1].split('_')
            command[1] = f"{c[0]}_{c[1]}_1"
        await choose_day(None,state,command[1])
    elif command[0] == 2:
        await choose_doctor_by_bot(message, state)
    elif command[0] == 3:
        if command[1] is None:
            if str(message.from_user.id) in [str(a[0]) for a in list(db_scripts.get_doctors_id())]:
                await bot.send_message(message.from_user.id, text = 'Проверьте введенную дату', reply_markup = kb_main_menu_admin)
            else:
                await bot.send_message(message.from_user.id, text = 'Проверьте введенную дату', reply_markup = kb_main_menu)
        else:
            if command[1].split('_')[-1] == '-1':
                await bot.send_message(message.from_user.id, text = 'Не удалось распознать врача, направляю к терапевту')
                c = command[1].split('_')
                command[1] = f"{c[0]}_{c[1]}_{c[2]}_1"
            now = datetime.datetime.now()
            H = now.strftime('%H')
            M = now.strftime('%M')
            t = int(H)*2+int(M)/30.0
            times = db_scripts.get_times(command[1].split('_')[-1],command[1].split('_')[-2],t)
            if len(times) > 0:
                await choose_time(None, state, command[1])
            else:
                await bot.send_message(message.from_user.id, text = 'На данный день нет доступных записей :с')


#Сохранение введенных симптомов, их обработка
async def take_symptoms(message: types.Message, state: FSMContext):
    await FSMmain.choose_day.set()
    id = choose_doctor(message.text)
    await bot.send_message(message.from_user.id, text =  f'Рекоммендуем вам записаться к {db_scripts.get_info_doctor(id)[0][1]}у, выберите удобный день:', reply_markup = choose_day_kb.make_keyBoard(id,1))

def register_handlers_forsasha(dp: Dispatcher):
    dp.register_message_handler(get_command, state=FSMmain.main_menu)
    dp.register_message_handler(take_symptoms, state = FSMmain.symptoms)
