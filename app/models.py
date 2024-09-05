# app/models.py

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./test.db"  # Beispielhafte SQLite-Datenbank, anpassbar

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    file_path = Column(String, index=True)  # Speichert den Dateipfad des GLTF-Modells


def init_db():
    # Drop the old table if it exists
    Base.metadata.drop_all(bind=engine)
    # Create the new table
    Base.metadata.create_all(bind=engine)


# Add this function to handle database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
