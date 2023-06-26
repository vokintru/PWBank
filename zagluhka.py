from aiogram.utils.callback_data import CallbackData
from aiogram import Bot, Dispatcher, executor, types
import logging

bot = Bot(token='5770955541:AAGsRfapWCpGPgLsKw0QU27Cmd0paAPMk4M') #main
#bot = Bot(token='5981619355:AAEDR3MAgSWW2TMx_yOkTcPlMWnP3HOZMKE') #beta
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

@dp.message_handler()
async def send_message(msg: types.Message):
    await msg.reply('Бот на серьёзных тех. работах! Подробние: https://t.me/PWBankInfo/39')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)