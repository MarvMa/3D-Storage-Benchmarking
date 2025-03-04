from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Instance, Project, Item


class InstanceService:
    """
    Service layer for managing instances and their associated projects and items.

    This class provides methods for creating, updating, retrieving, and deleting instances of items within projects.
    """

    @staticmethod
    def create_instance(db: Session, instance_data):
        """
        Create a new instance associated with a project and an item.

        Parameters:
            - db: Database session.
            - instance_data: The data for the instance, including project_id, item_id, and transformation details.

        Returns:
            - The newly created instance with its details.

        Raises:
            - HTTPException with status code 404 if the project or item is not found.
        """
        ensure_project_or_item_exists(db, project_id=instance_data.project_id, item_id=instance_data.item_id)
        new_instance = Instance(
            project_id=instance_data.project_id,
            item_id=instance_data.item_id,
            position_x=instance_data.position_x,
            position_y=instance_data.position_y,
            position_z=instance_data.position_z,
            rotation_x=instance_data.rotation_x,
            rotation_y=instance_data.rotation_y,
            rotation_z=instance_data.rotation_z,
            scale_x=instance_data.scale_x,
            scale_y=instance_data.scale_y,
            scale_z=instance_data.scale_z
        )
        db.add(new_instance)
        db.commit()
        db.refresh(new_instance)
        return new_instance

    @staticmethod
    def update_instance(db: Session, instance_id: int, instance_data):
        """
        Update an existing instance with new transformation details and project/item associations.

        Parameters:
            - db: Database session.
            - instance_id: The ID of the instance to update.
            - instance_data: The updated data for the instance.

        Returns:
            - The updated instance with its new details.

        Raises:
            - HTTPException with status code 404 if the instance, project, or item is not found.
        """
        instance = db.query(Instance).filter(Instance.id == instance_id).first()
        if not instance:
            raise HTTPException(status_code=404, detail="Instance not found")
        ensure_project_or_item_exists(db, instance_data.project_id, instance_data.item_id)
        for attr, value in (instance_data.items()):
            setattr(instance, attr, value)
        db.commit()
        db.refresh(instance)
        return instance

    @staticmethod
    def get_instance(db: Session, instance_id: int):
        """
        Retrieve an instance by its ID along with its details.

        Parameters:
            - db: Database session.
            - instance_id: The unique ID of the instance to retrieve.

        Returns:
            - The instance's details.

        Raises:
            - HTTPException with status code 404 if the instance is not found.
        """
        instance = db.query(Instance).filter(Instance.id == instance_id).first()
        if instance is None:
            raise HTTPException(status_code=404, detail="Instance not found")
        return instance

    @staticmethod
    def list_instances(db: Session):
        """
        List all instances in the database.

        Parameters:
            - db: Database session.

        Returns:
            - A list of all instances with their details.
        """
        instances = db.query(Instance).all()
        return instances

    @staticmethod
    def delete_instance(db: Session, instance_id: int):
        """
        Delete an instance by its ID.

        Parameters:
            - db: Database session.
            - instance_id: The unique ID of the instance to delete.

        Returns:
            - A message confirming that the instance has been deleted successfully.

        Raises:
            - HTTPException with status code 404 if the instance is not found.
        """
        instance = db.query(Instance).filter(Instance.id == instance_id).first()
        if instance is None:
            raise HTTPException(status_code=404, detail="Instance not found")
        db.delete(instance)
        db.commit()
        return {"message": "Instance deleted successfully"}


def ensure_project_or_item_exists(db: Session, project_id: int = None, item_id: int = None):
    """
    Ensures that either the project or item exists in the database.
    Raises HTTPException (404) if neither exists.

    Args:
        db (Session): The database session.
        project_id (int, optional): The ID of the project to check.
        item_id (int, optional): The ID of the item to check.

    Returns:
        None: Raises an exception if neither exists.
    """
    project_exists = db.query(Project).filter(Project.id == project_id).first() if project_id else None
    item_exists = db.query(Item).filter(Item.id == item_id).first() if item_id else None

    if project_exists is None and item_exists is None:
        raise HTTPException(status_code=404, detail="Neither Project nor Item found")
