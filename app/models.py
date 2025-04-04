import enum
import os

from sqlalchemy import Column, Integer, String, inspect, LargeBinary, Enum
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

# Database-Connection Settings and Session setup
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(
    DATABASE_URL,
    pool_size=30,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=300
)

SessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)
Base = declarative_base()


class StorageTypeEnum(str, enum.Enum):
    """Enum representing available storage backend types for persistent data storage.

       Values:
           db: Relational database storage (BLOB in database)
           file: Local filesystem storage
           minio:  object storage (MinIO implementation)
       """
    db = "db"
    file = "file"
    minio = "minio"


class Item(Base):
    """Database model for storing metadata and references to persisted files.

    Attributes:
        id (int): Auto-incremented primary key identifier
        name (str): Human-readable display name for the file
        filename (str): Original filename with extension
        storage_type (StorageTypeEnum): Storage backend used for this file
        path_or_key (str | None):
            - Filesystem path (for 'file' storage_type)
            - Object storage key (for 'minio' storage_type)
            - Null for 'db' storage_type
        content (bytes | None):
            - Raw file content (only populated for 'db' storage_type)
            - Null for 'file' and 'minio' storage_types
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    storage_type = Column(Enum(StorageTypeEnum), nullable=False)
    path_or_key = Column(String, nullable=True)  # für file/minio
    content = Column(LargeBinary, nullable=True)  # nur für db


async def init_db():
    async with engine.begin() as conn:
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
