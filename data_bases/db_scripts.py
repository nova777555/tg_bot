from os import curdir
import sqlite3 as sq

#Создание таблицы с пользователями
def db_load():
    global base, cur, doctors
    base = sq.connect('bd.db')
    cur = base.cursor()
    doctors = get_doctors()
    if base:
        print("Data base has loaded succesfully!")


#Добавление нового пользвателя в БД в таблицу users
async def add_user(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?)', tuple(data.values()))
        base.commit()

#Получение списка врачей
def get_doctors():
    base = sq.connect('bd.db')
    cur = base.cursor()
    cur.execute('SELECT fio, prof FROM doctors')
    return cur.fetchall()