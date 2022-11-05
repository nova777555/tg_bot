from aiogram import types, Dispatcher
from create_bot import bot, dp

async def command_forsasha(message : types.Message):
    await bot.send_message(message.from_user.id,'Иди нахуй, Саша!')

def register_handlers_forsasha(dp : Dispatcher):
    dp.register_message_handler(command_forsasha)