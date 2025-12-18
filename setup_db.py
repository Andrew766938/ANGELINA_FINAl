#!/usr/bin/env python3
"""
🗄️ Скрипт для инициализации БД при первом запуске проекта

Этот скрипт:
1. Создает/пересоздает БД
2. Применяет все миграции
3. Загружает тестовые данные (опционально)

Использование:
    python setup_db.py              # Применить миграции
    python setup_db.py --reset      # Сбросить БД и создать заново
    python setup_db.py --seed       # Добавить тестовые данные
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path

# Добавь проект в path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database.database import Base, get_session
from app.models.flight import FlightModel, AirportModel
from app.models.booking import BookingModel
from app.models.users import UserModel
from app.models.roles import RoleModel
from datetime import datetime


async def reset_database():
    """🔴 Удалить все таблицы и БД"""
    print("\n🔴 Сброс БД...")
    
    # Получи путь к БД
    db_path = settings.DB_NAME
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"✅ Удалена БД: {db_path}")
    else:
        print(f"ℹ️  БД не найдена: {db_path}")


async def create_tables():
    """📝 Создать все таблицы"""
    print("\n📝 Создание таблиц...")
    
    engine = create_async_engine(
        settings.get_db_url,
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("✅ Таблицы созданы")


async def seed_data():
    """🌱 Загрузить тестовые данные"""
    print("\n🌱 Загрузка тестовых данных...")
    
    engine = create_async_engine(
        settings.get_db_url,
        echo=False,
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Проверь не загружены ли уже данные
        result = await session.execute(text("SELECT COUNT(*) FROM airports"))
        count = result.scalar()
        
        if count > 0:
            print("ℹ️  Тестовые данные уже загружены")
            await engine.dispose()
            return
        
        # Создай тестовые аэропорты
        airports = [
            AirportModel(
                code='MOW',
                name='Шереметьево',
                city='Москва',
                country='Россия'
            ),
            AirportModel(
                code='SPB',
                name='Пулково',
                city='Санкт-Петербург',
                country='Россия'
            ),
            AirportModel(
                code='KZN',
                name='Казань',
                city='Казань',
                country='Россия'
            ),
            AirportModel(
                code='SVX',
                name='Кольцово',
                city='Екатеринбург',
                country='Россия'
            ),
            AirportModel(
                code='YKA',
                name='Площадь Ленина',
                city='Якутск',
                country='Россия'
            ),
        ]
        
        session.add_all(airports)
        await session.commit()
        
        print(f"✅ Загружено {len(airports)} аэропортов")
    
    await engine.dispose()


async def apply_migrations():
    """🔄 Применить миграции (через Alembic)"""
    print("\n🔄 Применение миграций...")
    
    import subprocess
    
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=Path(__file__).parent,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Миграции применены успешно")
        if result.stdout:
            print(result.stdout)
    else:
        print("❌ Ошибка при применении миграций:")
        print(result.stderr)
        raise RuntimeError("Миграции не применены")


async def check_database():
    """✅ Проверить что БД работает"""
    print("\n✅ Проверка БД...")
    
    try:
        engine = create_async_engine(
            settings.get_db_url,
            echo=False,
        )
        
        async with engine.begin() as conn:
            result = await conn.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table';"
            ))
            tables = [row[0] for row in result.fetchall()]
        
        await engine.dispose()
        
        if tables:
            print(f"✅ Таблицы найдены: {', '.join(tables)}")
            return True
        else:
            print("⚠️  Таблицы не найдены")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False


async def main():
    parser = argparse.ArgumentParser(
        description="🗄️ Инициализация базы данных"
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Сбросить БД и пересоздать"
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Загрузить тестовые данные"
    )
    parser.add_argument(
        "--migrate",
        action="store_true",
        help="Применить миграции через Alembic"
    )
    
    args = parser.parse_args()
    
    print("""
╔═══════════════════════════════════════╗
║   🗄️  Setup Database                  ║
╚═══════════════════════════════════════╝
    """)
    
    try:
        # Если флаг --reset, удали БД
        if args.reset:
            await reset_database()
        
        # Если есть флаг --migrate, примени миграции
        if args.migrate:
            await apply_migrations()
        else:
            # Иначе создай таблицы напрямую
            await create_tables()
        
        # Если флаг --seed, загрузи тестовые данные
        if args.seed:
            await seed_data()
        
        # Проверь что БД работает
        success = await check_database()
        
        if success:
            print("""
╔═══════════════════════════════════════╗
║   ✅ БД готова к использованию!       ║
╚═══════════════════════════════════════╝
            """)
        else:
            print("""
╔═══════════════════════════════════════╗
║   ⚠️  Проверь логи выше               ║
╚═══════════════════════════════════════╝
            """)
            sys.exit(1)
    
    except Exception as e:
        print(f"""
╔═══════════════════════════════════════╗
║   ❌ Ошибка: {str(e)[:30]}...          ║
╚═══════════════════════════════════════╝
        """)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    # Проверь что запускается из нужной директории
    if not Path("app").exists():
        print("❌ Ошибка: запусти скрипт из корня проекта")
        print("   Правильно: python setup_db.py")
        sys.exit(1)
    
    asyncio.run(main())
