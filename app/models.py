import enum
import os

from sqlalchemy import Column, Integer, String, inspect, LargeBinary, Enum
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

# Database-Connection Settings and Session setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(
    DATABASE_URL,
    pool_size=30,  # Maximale ständige Verbindungen
    max_overflow=10,  # Temporäre zusätzliche Verbindungen
    pool_timeout=30,  # Timeout für Verbindungsanfragen
    pool_recycle=300  # Verbindungen nach 5 Minuten neu aufbauen
)

SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)
Base = declarative_base()


class StorageTypeEnum(str, enum.Enum):
    db = "db"
    file = "file"
    minio = "minio"


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    storage_type = Column(Enum(StorageTypeEnum), nullable=False)
    path_or_key = Column(String, nullable=True)  # für file/minio
    content = Column(LargeBinary, nullable=True)  # nur für db


async def init_db():
    async with engine.begin() as conn:
        # Prüfe, ob die Tabelle existiert (mit synchroner Verbindung)
        table_exists = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).has_table("items")
        )

        if not table_exists:
            await conn.run_sync(Base.metadata.create_all)
            print("Datenbank-Schema erfolgreich erstellt.")
        else:
            print("Schema existiert bereits.")


async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
