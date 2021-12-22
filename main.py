import logging
from os import getenv
from sys import exit as exit_f
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import BotBlocked

bot_token = getenv("BOT_TOKEN")
if not bot_token:
    exit_f("Error: no token provided")

bot = Bot(token=bot_token)
dp = Dispatcher(bot)
logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
@dp.errors_handler(exception=BotBlocked)
async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    print(f"Bot has been blocked\nMessage: {update}\nError: {exception}")
    return True
@dp.message_handler()
async def replier(message: types.Message):
    await message.answer(message.text)
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)