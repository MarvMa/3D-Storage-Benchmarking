# app/models.py
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class ExampleModel(Base):
    __tablename__ = 'examples'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

# SQLite-Engine und Session erstellen
engine = create_engine('sqlite:///app.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
