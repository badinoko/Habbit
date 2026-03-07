# ruff: noqa: E402
import asyncio
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

from faker import Faker
from sqlalchemy import select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# импортируй свои сущности и создание сессии
from src.database.connection import AsyncSessionLocal as async_session_maker
from src.database.models import Priority, Task, Theme

fake = Faker("ru_RU")

N = 350


async def seed() -> None:
    async with async_session_maker() as session:  # type: AsyncSession
        # 1) убедимся, что есть priorities
        priorities = (await session.execute(select(Priority))).scalars().all()
        if not priorities:
            priorities = [
                Priority(id=uuid4(), name="низкий", weight=1, color="#00FF00"),
                Priority(id=uuid4(), name="средний", weight=2, color="#FFFF00"),
                Priority(id=uuid4(), name="высокий", weight=3, color="#FF0000"),
            ]
            session.add_all(priorities)
            await session.flush()  # чтобы появились id

        # 2) темы (если нет — создадим несколько)
        themes = (await session.execute(select(Theme))).scalars().all()
        if not themes:
            themes = [
                Theme(id=uuid4(), name="Дом", color="#A1C3FF"),
                Theme(id=uuid4(), name="Работа", color="#FFD5A1"),
                Theme(id=uuid4(), name="Здоровье", color="#B7F0C0"),
                Theme(id=uuid4(), name="Учёба", color="#E7C6FF"),
            ]
            session.add_all(themes)
            await session.flush()

        now = datetime.utcnow()

        tasks = []
        for i in range(N):
            pr = random.choice(priorities)
            th = random.choice([*themes, None, None])  # иногда без темы
            created_at = now - timedelta(
                days=random.randint(0, 60), minutes=random.randint(0, 6000)
            )

            # примерно 35% выполненных
            completed = random.random() < 0.35
            completed_at = (
                (created_at + timedelta(hours=random.randint(1, 72)))
                if completed
                else None
            )

            tasks.append(
                Task(
                    name=f"Задача {i + 1}: {fake.sentence(nb_words=4)[:20]}",
                    description=fake.text(max_nb_chars=200),
                    theme_id=th.id if th else None,
                    priority_id=pr.id,
                    completed_at=completed_at,
                    created_at=created_at,
                    updated_at=created_at + timedelta(hours=random.randint(0, 48)),
                )
            )

        session.add_all(tasks)
        await session.commit()
        print(f"Inserted: {N} tasks")


if __name__ == "__main__":
    asyncio.run(seed())
