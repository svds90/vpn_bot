from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from dotenv import load_dotenv
import os
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv("BOT_TOKEN"))  # type: ignore
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("hi")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
