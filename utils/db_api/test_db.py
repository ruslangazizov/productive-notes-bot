import asyncio

from utils.db_api.postgres import Database

db = Database()


async def test():
    await db.create_pool()
    await db.create_table_users()
    await db.delete_all_users()
    users = await db.select_all_users()
    print(f"До добавления пользователей {users=}")
    await db.add_user("full_name1", "name1", 1)
    await db.add_user("full_name2", "name2", 2)
    await db.add_user("full_name3", "name3", 3)
    await db.add_user("full_name4", "name4", 4)
    await db.add_user("full_name5", "name5", 5)

    users = await db.select_all_users()
    print(f"После добавления пользователей {users=}")
    user = await db.select_user(username="name2", telegram_id=2)
    print(f"Получил пользователя {user}")


loop = asyncio.get_event_loop()
loop.run_until_complete(test())
