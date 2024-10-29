import asyncio
import logging
import sys
from bot_token import TOKEN
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from db import add_to_database, add_scores_to_database, get_scores_from_database

TOKEN = TOKEN

dp = Dispatcher()


class Registration(StatesGroup):
    waiting_for_first_name = State()
    waiting_for_last_name = State()


class EnterScores(StatesGroup):
    waiting_for_scores = State()


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


@dp.message(Command("enter_scores"))
async def cmd_enter_scores(message: Message, state: FSMContext):
    await message.answer("Введите сумму баллов ЕГЭ:")
    await state.set_state(EnterScores.waiting_for_scores)


@dp.message(F.text, EnterScores.waiting_for_scores)
async def process_scores(message: Message, state: FSMContext):
    scores = message.text
    telegram_id = message.from_user.id

    # Вызов функции для добавления данных в базу данных
    await add_scores_to_database(telegram_id, scores)

    await message.answer(f"Баллы сохранены: {scores}")
    await state.clear()


@dp.message(Command("view_scores"))
async def cmd_view_scores(message: Message):
    telegram_id = message.from_user.id

    # Вызов функции для получения данных из базы данных
    scores = await get_scores_from_database(telegram_id)

    if scores:
        await message.answer(f"Ваши баллы ЕГЭ: {scores}")
    else:
        await message.answer("У вас нет сохраненных баллов.")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
