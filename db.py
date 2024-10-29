import aiosqlite
import datetime


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


async def add_scores_to_database(telegram_id, scores):
    async with aiosqlite.connect("students.db") as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS scores (telegram_id BIGINT, scores TEXT)"
        )
        await db.execute(
            "INSERT INTO scores (telegram_id, scores) VALUES (?, ?)",
            (telegram_id, scores),
        )
        await db.commit()


async def get_scores_from_database(telegram_id):
    async with aiosqlite.connect("students.db") as db:
        cursor = await db.execute(
            "SELECT scores FROM scores WHERE telegram_id = ?", (telegram_id,)
        )
        data = await cursor.fetchone()
        if data:
            return data[0]
        return None
