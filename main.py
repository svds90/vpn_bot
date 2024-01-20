from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import asyncio
import logging
from settings.config import *

logging.basicConfig(level=logging.INFO)

bot = Bot(token=bot_token)  # type: ignore
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("hi")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
