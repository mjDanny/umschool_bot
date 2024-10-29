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


# Определение состояний для регистрации и ввода баллов ЕГЭ
class Registration(StatesGroup):
    waiting_for_first_name = State()
    waiting_for_last_name = State()


class EnterScores(StatesGroup):
    waiting_for_math = State()
    waiting_for_physics = State()
    waiting_for_russian = State()


# Обработчик команды /start
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Привет! Зарегистрируйся или войди в свой аккаунт с помощью команды /register."
    )


# Обработчик команды /register
@dp.message(Command("register"))
async def cmd_register(message: Message, state: FSMContext):
    await message.answer("Введите имя:")
    await state.set_state(Registration.waiting_for_first_name)


# Обработчик ввода имени
@dp.message(F.text, Registration.waiting_for_first_name)
async def process_first_name(message: Message, state: FSMContext):
    first_name = message.text
    await state.update_data(first_name=first_name)
    await message.answer("Введите фамилию:")
    await state.set_state(Registration.waiting_for_last_name)


# Обработчик ввода фамилии
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


# Обработчик команды /enter_scores
@dp.message(Command("enter_scores"))
async def cmd_enter_scores(message: Message, state: FSMContext):
    await message.answer("Введите баллы по математике:")
    await state.set_state(EnterScores.waiting_for_math)


# Обработчик ввода баллов по математике
@dp.message(F.text, EnterScores.waiting_for_math)
async def process_math_score(message: Message, state: FSMContext):
    math_score = message.text
    await state.update_data(math_score=math_score)
    await message.answer("Введите баллы по физике:")
    await state.set_state(EnterScores.waiting_for_physics)


# Обработчик ввода баллов по физике
@dp.message(F.text, EnterScores.waiting_for_physics)
async def process_physics_score(message: Message, state: FSMContext):
    physics_score = message.text
    await state.update_data(physics_score=physics_score)
    await message.answer("Введите баллы по русскому языку:")
    await state.set_state(EnterScores.waiting_for_russian)


# Обработчик ввода баллов по русскому языку
@dp.message(F.text, EnterScores.waiting_for_russian)
async def process_russian_score(message: Message, state: FSMContext):
    russian_score = message.text
    user_data = await state.get_data()
    math_score = user_data.get("math_score")
    physics_score = user_data.get("physics_score")
    telegram_id = message.from_user.id

    # Вызов функции для добавления данных в базу данных
    await add_scores_to_database(telegram_id, math_score, physics_score, russian_score)

    await message.answer(
        f"Баллы сохранены: Математика: {math_score}, Физика: {physics_score}, Русский язык: {russian_score}"
    )
    await state.clear()


# Обработчик команды /view_scores
@dp.message(Command("view_scores"))
async def cmd_view_scores(message: Message):
    telegram_id = message.from_user.id

    # Вызов функции для получения данных из базы данных
    scores = await get_scores_from_database(telegram_id)

    if scores:
        await message.answer(
            f"Ваши баллы ЕГЭ: Математика: {scores['math_score']}, Физика: {scores['physics_score']}, Русский язык: {scores['russian_score']}"
        )
    else:
        await message.answer("У вас нет сохраненных баллов.")


# Запускаем бота
async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
