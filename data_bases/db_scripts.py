from os import curdir
import sqlite3 as sq
import datetime

#Создание таблицы с пользователями
def db_load():
    global base, cur, doctors
    base = sq.connect('bd.db')
    cur = base.cursor()
    doctors = get_doctors()
    if base:
        print("Data base has loaded succesfully!")

#Создание таблицы с окнами. Аргумент а - список по количеству докторов семи списков(дни недели) 
#по два числа - начало рабочего дня и окончание (одна единица = 30 минут), если день нерабочий, ставим -1
#Так, например, запись расписания для одного врача может выглядеть как
#[[[18,31],[-1,-1],[18,31],[-1,-1],[18,31],[-1,-1],[-1,-1]]],
#которая означает рабочее время: пн, ср, пт 9:00-16:00
def new_appointments_timetable(a):
    translate_dow = {
        'Monday' : 'Понедельник',
        'Tuesday' : 'Вторник',
        'Wednesday' : 'Среда',
        'Thursday' : 'Четверг',
        'Friday' : 'Пятница',
        'Saturday' : 'Суббота',
        'Sunday' : 'Воскресенье'
    }
    base = sq.connect('bd.db')
    cur = base.cursor()
    WEEKS_COUNT = 30
    DELTA = datetime.timedelta(
        days=1
    )
    date = datetime.datetime.now()
    while date.strftime('%A') != 'Sunday':
        date -= DELTA
    for id in range(len(a)):
        for week_number in range(WEEKS_COUNT):
            for dow in range(7):
                date += DELTA
                if a[id][dow][0] == -1: 
                    continue
                for time in range(a[id][dow][0],a[id][dow][1]+1):
                    cur.execute('INSERT INTO appointments (date, dayweek, time, doctor) VALUES (?, ?, ?, ?)', 
                    tuple([date.strftime('%Y')+'-'+date.strftime('%m')+'-'+date.strftime('%d'), 
                    translate_dow[date.strftime('%A')], time, id+1]))
        date = datetime.datetime.now()
    base.commit()

#Добавление нового пользвателя в БД в таблицу users
async def add_user(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?)', tuple(data.values()))
        base.commit()

#Оформление записи
async def make_appointment(state, patient):
    async with state.proxy() as data:
        doctor = data['id']
        date = data['date']
        date = f'\'{date}\''
        time = data['time'] 
        cur.execute(f'UPDATE appointments SET patient = {patient} WHERE doctor = {doctor} AND date = {date} AND time = {time}')
        base.commit()

#Отмена записи
async def cancel_appointment(id):
    base = sq.connect('bd.db')
    cur = base.cursor()
    cur.execute(f'UPDATE appointments SET patient = NULL WHERE id = {id}')
    base.commit()


#Получение списка врачей
def get_doctors():
    base = sq.connect('bd.db')
    cur = base.cursor()
    cur.execute('SELECT fio, prof FROM doctors')
    return cur.fetchall()

#Получение списка рабочих дней выбранного врача
def get_days(id, page):
    base = sq.connect('bd.db')
    cur = base.cursor()
    cur.execute('SELECT DISTINCT date, dayweek FROM appointments WHERE date > datetime(\'now\', \'start of day\') AND doctor = '+str(id))
    return list(cur.fetchall())[(page-1)*10:page*10]

#Получение списка свободных окон
def get_times(id,date):
    base = sq.connect('bd.db')
    cur = base.cursor()
    date = f'\'{date}\''
    cur.execute(f'SELECT time FROM appointments WHERE doctor = {str(id)} AND patient IS NULL AND date = date({date})')
    return list(cur.fetchall())

#Получение информации о докторе по id
def get_info_doctor(id):
    base = sq.connect('bd.db')
    cur = base.cursor()
    cur.execute(f'SELECT fio, prof FROM doctors WHERE id = {id}')
    return list(cur.fetchall())

#Получение записи по id
def get_info_appointment(id):
    base = sq.connect('bd.db')
    cur = base.cursor()
    cur.execute(f'SELECT date,time,doctor,patient FROM appointments WHERE id = {id}')
    return list(cur.fetchall())

#Поиск записей пациента
def get_appointments(patient):
    base = sq.connect('bd.db')
    cur = base.cursor()
    cur.execute(f'SELECT id FROM appointments WHERE patient = {patient}')
    return list(cur.fetchall())

