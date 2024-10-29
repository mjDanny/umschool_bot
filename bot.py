import asyncio
import datetime
import logging
import sys

import aiosqlite

from bot_token import TOKEN
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

TOKEN = TOKEN

dp = Dispatcher()


async def add_to_database(telegram_id, username):
    async with aiosqlite.connect("students.db") as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS users (telegram_id BIGINT , username TEXT, date TEXT)"
        )
        cursor = await db.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        data = await cursor.fetchone()
        if data is not None:
            print("None")
            return
    date = f"{datetime.date.today()}"
    async with aiosqlite.connect("students.db") as db:
        await db.execute(
            "INSERT INTO users (telegram_id, username, date) VALUES (?,?,?)",
            (telegram_id, username, date),
        )
        await db.commit()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Hello!")
    telegram_id = message.from_user.id
    username = message.from_user.username
    await add_to_database(telegram_id, username)


@dp.message(F.text, Command('reg'))
async def test(message: Message) -> None:
    await message.answer("регайся")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
