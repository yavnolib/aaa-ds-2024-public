from dataclasses import dataclass

import asyncpg
import asyncio


@dataclass
class ItemEntry:
    item_id: int
    user_id: int
    title: str
    description: str


class ItemStorage:
    def __init__(self):
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        # We initialize client here, because we need to connect it,
        # __init__ method doesn't support awaits.
        #
        # Pool will be configured using env variables.
        self._pool = await asyncpg.create_pool()

    async def disconnect(self) -> None:
        # Connections should be gracefully closed on app exit to avoid
        # resource leaks.
        await self._pool.close()

    async def create_tables_structure(self) -> None:
        """
        Создайте таблицу items со следующими колонками:
         item_id (int) - обязательное поле, значения должны быть уникальными
         user_id (int) - обязательное поле
         title (str) - обязательное поле
         description (str) - обязательное поле
        """
        # In production environment we will use migration tool
        # like https://github.com/pressly/goose
        # YOUR CODE GOES HERE
        await self._pool.execute(
                """
                CREATE TABLE IF NOT EXISTS items (
                    item_id INT PRIMARY KEY,
                    user_id INT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL
                )
                """
            )
            
    async def save_items(self, items: list[ItemEntry]) -> None:
        """
        Напишите код для вставки записей в таблицу items одним запросом, цикл
        использовать нельзя.
        """
        # Don't use str-formatting, query args should be escaped to avoid
        # sql injections https://habr.com/ru/articles/148151/.
        # YOUR CODE GOES HERE
        query = """
                    INSERT INTO items (item_id, user_id, title, description)
                    VALUES ($1, $2, $3, $4)
                """

        values = [(item.item_id, item.user_id, item.title, item.description) for item in items]

        await self._pool.executemany(query, values)


    async def find_similar_items(
        self, user_id: int, title: str, description: str
    ) -> list[ItemEntry]:
        """
        Напишите код для поиска записей, имеющих указанные user_id, title и description.
        """
        # YOUR CODE GOES HERE
        query = """
                SELECT * FROM items
                WHERE user_id = $1 AND title = $2 AND description = $3
            """

        rows = await self._pool.fetch(query, user_id, title, description)

        return [ItemEntry(**row) for row in rows]

async def main():
    its = ItemStorage()
    await its.connect()
    await its.create_tables_structure()
    await its.save_items([ItemEntry(item_id=1, user_id=7, title="test1", description="test2")])

        
if __name__ == '__main__':
    asyncio.run(main())