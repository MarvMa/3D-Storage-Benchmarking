import enum
import os

from sqlalchemy import Column, Integer, String, create_engine, inspect, LargeBinary, Enum
from sqlalchemy.orm import sessionmaker, declarative_base

# Database-Connection Settings and Session setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://arpas_user:securepassword@postgres:5432/arpas_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
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


def init_db():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    if not existing_tables:
        try:
            Base.metadata.create_all(bind=engine)
            print("Datenbank-Schema erfolgreich erstellt.")
        except Exception as e:
            print(f"Fehler beim Erstellen des Schemas: {str(e)}")
    else:
        print("Schema existiert bereits. Keine Aktion erforderlich.")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
