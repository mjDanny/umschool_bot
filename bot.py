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
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

TOKEN = TOKEN

dp = Dispatcher()


class Registration(StatesGroup):
    waiting_for_first_name = State()
    waiting_for_last_name = State()


async def add_to_database(telegram_id, first_name, last_name):
    async with aiosqlite.connect("students.db") as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS users (telegram_id BIGINT, first_name TEXT, last_name TEXT, date TEXT)"
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
            "INSERT INTO users (telegram_id, first_name, last_name, date) VALUES (?,?,?,?)",
            (telegram_id, first_name, last_name, date),
        )
        await db.commit()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Привет! Зарегистрируйся или войди в свой аккаунт с помощью команды /register."
    )


@dp.message(Command("register"))
async def cmd_register(message: Message, state: FSMContext):
    await message.answer("Введите имя:")
    await state.set_state(Registration.waiting_for_first_name)


@dp.message(F.text, Registration.waiting_for_first_name)
async def process_first_name(message: Message, state: FSMContext):
    first_name = message.text
    await state.update_data(first_name=first_name)
    await message.answer("Введите фамилию:")
    await state.set_state(Registration.waiting_for_last_name)


@dp.message(F.text, Registration.waiting_for_last_name)
async def process_last_name(message: Message, state: FSMContext):
    last_name = message.text
    user_data = await state.get_data()
    first_name = user_data.get("first_name")
    telegram_id = message.from_user.id

    # Вызов функции для добавления данных в базу данных
    await add_to_database(telegram_id, first_name, last_name)

    await message.answer(
        f"Регистрация завершена. Ваши данные: {first_name} {last_name}"
    )
    await state.clear()


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
