from typing import Optional, List

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config, DEFAULT_CATEGORIES


class Database:
    def __init__(self, pool):
        self.pool: Optional[Pool] = pool

    @classmethod
    async def create_pool(cls):
        pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )
        return cls(pool)

    async def execute(self, command: str, *args, fetch_all=False, fetch_row=False,
                      fetch_val=False, execute=False):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch_all:
                    result = await connection.fetch(command, *args)
                elif fetch_row:
                    result = await connection.fetchrow(command, *args)
                elif fetch_val:
                    result = await connection.fetchval(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username VARCHAR(255),
        telegram_id BIGINT NOT NULL UNIQUE
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_notes(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Notes (
        id SERIAL PRIMARY KEY,
        user_tg_id BIGINT NOT NULL REFERENCES Users(telegram_id),
        text TEXT NOT NULL,
        category VARCHAR(255) NOT NULL
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_categories(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Categories (
        id SERIAL PRIMARY KEY,
        user_tg_id BIGINT NOT NULL REFERENCES Users(telegram_id),
        name VARCHAR(255) NOT NULL
        );
        """
        await self.execute(sql, execute=True)

    async def create_standard_tables(self):
        await self.create_table_users()
        await self.create_table_notes()
        await self.create_table_categories()

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ${idx + 1}" for idx, item in enumerate(parameters)
        ])
        return sql, tuple(parameters.values())

    # section: Working with table Users

    async def add_user(self, full_name: str, username: str, telegram_id: int):
        sql = "INSERT INTO Users (full_name, username, telegram_id) VALUES ($1, $2, $3) returning *"
        user = await self.execute(sql, full_name, username, telegram_id, fetch_row=True)
        await self.add_default_categories_for_user(telegram_id)
        return user

    async def select_all_users(self):
        sql = "SELECT * FROM Users"
        return await self.execute(sql, fetch_all=True)

    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return await self.execute(sql, *parameters, fetch_row=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetch_val=True)

    async def update_user_username(self, username, telegram_id):
        sql = "UPDATE Users SET username = $1 WHERE telegram_id = $2"
        return await self.execute(sql, username, telegram_id, execute=True)

    # section: Working with table Notes

    async def add_note(self, telegram_id: int, category: str, note_text: str):
        sql = "INSERT INTO Notes (user_tg_id, text, category) VALUES ($1, $2, $3)"
        await self.execute(sql, telegram_id, note_text, category, execute=True)

    async def delete_note(self, telegram_id: int, category: str, note_text: str):
        sql = "DELETE FROM Notes WHERE user_tg_id = $1 AND text = $2 AND category = $3"
        await self.execute(sql, telegram_id, note_text, category, execute=True)

    async def delete_all_notes_in_category(self, category: str, telegram_id: int):
        sql = "DELETE FROM Notes WHERE user_tg_id = $1 AND category = $2"
        await self.execute(sql, telegram_id, category, execute=True)

    async def get_user_notes_in_category(self, telegram_id: int, category: str) -> List[str]:
        sql = "SELECT text FROM Notes WHERE "
        sql, parameters = self.format_args(sql, dict(user_tg_id=telegram_id, category=category))
        sql += " ORDER BY id DESC"
        user_notes_in_category = await self.execute(sql, *parameters, fetch_all=True)
        return [note.get("text") for note in user_notes_in_category]

    async def update_note_text(self, old_text: str, new_text: str, telegram_id: int, category: str):
        sql = "UPDATE Notes SET text = $1 WHERE user_tg_id = $2 AND text = $3 AND category = $4"
        await self.execute(sql, new_text, telegram_id, old_text, category, execute=True)

    # section: Working with table Categories

    async def add_default_categories_for_user(self, telegram_id: int):
        sql = "INSERT INTO Categories (user_tg_id, name) VALUES "
        values = ", ".join([
            f"({telegram_id}, '{category_name}')" for category_name in DEFAULT_CATEGORIES
        ])
        sql += values
        await self.execute(sql, execute=True)

    async def get_user_categories(self, telegram_id: int) -> List[str]:
        sql = "SELECT name FROM Categories WHERE user_tg_id = $1"
        user_categories = await self.execute(sql, telegram_id, fetch_all=True)
        return [note.get("name") for note in user_categories]

    async def category_is_present(self, telegram_id: int, category: str) -> bool:
        sql = "SELECT * FROM Categories WHERE user_tg_id = $1 and name = $2"
        categories = await self.execute(sql, telegram_id, category, fetch_all=True)
        return len(categories) > 0

    async def add_user_category(self, telegram_id: int, category: str) -> bool:
        category_is_already_present = await self.category_is_present(telegram_id, category)
        if not category_is_already_present:
            sql = "INSERT INTO Categories (user_tg_id, name) VALUES ($1, $2)"
            await self.execute(sql, telegram_id, category, execute=True)
        return not category_is_already_present

    async def delete_user_category(self, telegram_id: int, category: str):
        sql = "DELETE FROM Categories WHERE user_tg_id = $1 AND name = $2"
        await self.execute(sql, telegram_id, category, execute=True)
        await self.delete_all_notes_in_category(category, telegram_id)
