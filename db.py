import aiosqlite
import datetime

# Функция для добавления данных пользователя в базу данных
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

# Функция для добавления баллов ЕГЭ в базу данных
async def add_scores_to_database(telegram_id, math_score, physics_score, russian_score):
    async with aiosqlite.connect("students.db") as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS scores (telegram_id BIGINT, math_score TEXT, physics_score TEXT, russian_score TEXT)"
        )
        await db.execute(
            "INSERT INTO scores (telegram_id, math_score, physics_score, russian_score) VALUES (?, ?, ?, ?)",
            (telegram_id, math_score, physics_score, russian_score),
        )
        await db.commit()

# Функция для получения баллов ЕГЭ из базы данных
async def get_scores_from_database(telegram_id):
    async with aiosqlite.connect("students.db") as db:
        cursor = await db.execute(
            "SELECT math_score, physics_score, russian_score FROM scores WHERE telegram_id = ?",
            (telegram_id,),
        )
        data = await cursor.fetchone()
        if data:
            return {
                "math_score": data[0],
                "physics_score": data[1],
                "russian_score": data[2],
            }
        return None
