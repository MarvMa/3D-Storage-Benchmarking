from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine, LargeBinary
from sqlalchemy.orm import relationship, sessionmaker, declarative_base;

# Datenbankverbindungseinstellungen und Session-Setup
DATABASE_URL = "sqlite:///./arpas-dev.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Item(Base):
    """
      Represents a 3D object that can be managed within the application.

      Attributes:
          id (int): Unique identifier for the item.
          name (str): Name of the 3D object.
          description (str): Description of the 3D object.
          file_path (str): Path to the file where the 3D object is stored on the server.
          collections (List[CollectionItem]): Relationship to the CollectionItem class to associate items with collections.
      """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    file_path = Column(String, index=True)

    collections = relationship("CollectionItem", back_populates="item")


class Collection(Base):
    """
        Represents a collection of 3D objects.

        Attributes:
            id (int): Unique identifier for the collection.
            name (str): Name of the collection.
            description (str): Description of the collection.
            items (List[CollectionItem]): Relationship to the CollectionItem class to associate collections with items.
        """
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)

    items = relationship("CollectionItem", back_populates="collection")


class CollectionItem(Base):
    """
      Represents the association between a collection and an item, establishing a many-to-many relationship.

      Attributes:
          id (int): Unique identifier for the association.
          collection_id (int): Foreign key to the collection.
          item_id (int): Foreign key to the item.
          collection (Collection): Relationship to the Collection class.
          item (Item): Relationship to the Item class.
      """
    __tablename__ = "collection_items"

    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(Integer, ForeignKey('collections.id'))
    item_id = Column(Integer, ForeignKey('items.id'))

    collection = relationship("Collection", back_populates="items")
    item = relationship("Item", back_populates="collections")


class Project(Base):
    """
    Represents a project that can have multiple instances of 3D objects.

    Attributes:
        id (int): Unique identifier for the project.
        name (str): Name of the project.
        description (str): Description of the project.
        qr_code (bytes): QR code for the project stored as binary data.
        instances (List[Instance]): Relationship to the Instance class to associate projects with object instances.
    """
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True, doc="Unique identifier for the project.")
    name = Column(String, index=True, doc="Name of the project.")
    description = Column(String, index=True, doc="Description of the project.")
    qr_code = Column(LargeBinary, nullable=True, doc="QR code for the project stored as binary data.")
    qr_code_url = Column(String, index=True, doc="URL where the qr-code points to")

    instances = relationship("Instance", back_populates="project",
                             doc="Relationship with Instance to manage object instances.")


class Instance(Base):
    """
        Represents an instance of a 3D object within a project, including its transformations.

        Attributes:
            id (int): Unique identifier for the instance.
            project_id (int): Foreign key to the project.
            item_id (int): Foreign key to the item.
            position_x (float): X-coordinate for the position of the instance.
            position_y (float): Y-coordinate for the position of the instance.
            position_z (float): Z-coordinate for the position of the instance.
            rotation_x (float): Rotation around the X-axis for the instance.
            rotation_y (float): Rotation around the Y-axis for the instance.
            rotation_z (float): Rotation around the Z-axis for the instance.
            scale_x (float): Scaling factor along the X-axis.
            scale_y (float): Scaling factor along the Y-axis.
            scale_z (float): Scaling factor along the Z-axis.
            project (Project): Relationship to the Project class.
            item (Item): Relationship to the Item class.
        """
    __tablename__ = "instances"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    item_id = Column(Integer, ForeignKey('items.id'))
    position_x = Column(Float)
    position_y = Column(Float)
    position_z = Column(Float)
    rotation_x = Column(Float)
    rotation_y = Column(Float)
    rotation_z = Column(Float)
    scale_x = Column(Float)
    scale_y = Column(Float)
    scale_z = Column(Float)

    project = relationship("Project", back_populates="instances")
    item = relationship("Item")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
