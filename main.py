import asyncio
import logging
from os import getenv
from sys import exit as exit_f

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot.handlers.upload import register_handlers_upload, global_values_container

logger = logging.getLogger(__name__)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/upload", description="upload new file"),
        BotCommand(command="/cancel", description="cancel current action")
    ]
    await bot.set_my_commands(commands)


async def main():
    logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    bot_token = getenv("BOT_TOKEN")
    if not bot_token:
        exit_f("Error: no token provided")

    bot = Bot(token='bot_token')
    bot_info = await bot.get_me()
    global_values_container['bot_username'] = bot_info['username']

    dispatcher = Dispatcher(bot, storage=MemoryStorage())

    register_handlers_upload(dispatcher)
    await set_commands(bot)

    await dispatcher.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
