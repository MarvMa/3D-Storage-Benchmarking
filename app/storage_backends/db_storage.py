from sqlalchemy import create_engine, Column, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .base_interface import StorageInterface

Base = declarative_base()


class ThreeDObject(Base):
    __tablename__ = "three_d_objects"
    object_id = Column(String, primary_key=True)
    file_blob = Column(LargeBinary, nullable=False)


class DBStorage(StorageInterface):
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(self.database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def save_file(self, object_id: str, file: bytes) -> None:
        db_session = self.SessionLocal()
        try:
            existing_obj = db_session.query(ThreeDObject).filter_by(object_id=object_id).first()
            if existing_obj:
                # Update existing
                existing_obj.file_blob = file
            else:
                # Create new
                new_obj = ThreeDObject(object_id=object_id, file_blob=file)
                db_session.add(new_obj)

            db_session.commit()
        finally:
            db_session.close()

    def load_file(self, object_id: str) -> bytes | None:
        db_session = self.SessionLocal()
        try:
            obj = db_session.query(ThreeDObject).filter_by(object_id=object_id).first()
            return obj.file_blob
        finally:
            db_session.close()

    def delete_file(self, object_id: str) -> None:
        db_session = self.SessionLocal()
        try:
            obj = db_session.query(ThreeDObject).filter_by(object_id=object_id).first()
            if obj:
                db_session.delete(obj)
                db_session.commit()
        finally:
            db_session.close()
