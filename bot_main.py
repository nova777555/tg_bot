from aiogram.utils import executor
from create_bot import dp
from data_bases import db_scripts

#Регистрация всех обработчиков
#Важен порядок handler'ов
from handlers import registration
registration.register_handlers_registration(dp)
from handlers import main_h
main_h.register_handlers_menu(dp)
from handlers import forSasha
forSasha.register_handlers_forsasha(dp)

#Выполнение при старте бота
async def on_start(_):
    print('Bot is online')
    db_scripts.db_load()

#Запуск работы бота
executor.start_polling(dp,skip_updates = True, on_startup = on_start)