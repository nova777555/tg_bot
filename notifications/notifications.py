import datetime
from data_base import db_scripts
from create_bot import bot
import aioschedule
import asyncio


#Отправлений уведомлний всем пользователем с записью на завтрашний день
async def send_notifications():
    appointments_list = db_scripts.get_appointments_tomorrow()
    for appointment in appointments_list:
        data = list(*db_scripts.get_info_appointment(appointment[0]))
        doctor = list(*db_scripts.get_info_doctor(data[2]))
        time = data[1]
        h = int(time) // 2
        m = (int(time) % 2) * 30
        if m == 0: m = '00'
        await bot.send_message(data[3], text = f'Напоминаем о завтрашнем приеме к {doctor[0]} ({doctor[1]}) в {h}:{m}')

async def scheduler():
    NOTIFICATION_TIME = "17:00"
    aioschedule.every().day.at(NOTIFICATION_TIME).do(send_notifications)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)