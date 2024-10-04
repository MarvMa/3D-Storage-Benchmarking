from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models import get_db
from app.schemas import InstanceCreate, InstanceRead
from app.services.instances_service import InstanceService

router = APIRouter()


@router.post("/instances/", response_model=InstanceRead)
def create_instance(instance: InstanceCreate, db: Session = Depends(get_db)):
    """
    Create a new instance.

    This endpoint allows the creation of a new instance associated with a project and an item.
    The instance includes transformations like position, rotation, and scale.

    Parameters:
        - instance: JSON body containing the project_id, item_id, and transformation details.
        - db: Database session (injected).

    Returns:
        - The newly created instance, including its ID and associated project/item details.

    Raises:
        - 404 HTTPException if the project or item is not found.
    """
    return InstanceService.create_instance(db, instance)


@router.put("/instances/{instance_id}", response_model=InstanceRead)
def update_instance(instance_id: int, instance_update: InstanceCreate, db: Session = Depends(get_db)):
    """
    Update an existing instance.

    This endpoint allows updating an existing instance's transformation details (position, rotation, and scale),
    as well as changing the associated project or item.

    Parameters:
        - instance_id: The unique ID of the instance to update.
        - instance_update: JSON body containing the updated project_id, item_id, and transformation details.
        - db: Database session (injected).

    Returns:
        - The updated instance, including its new details.

    Raises:
        - 404 HTTPException if the instance, project, or item is not found.
    """
    return InstanceService.update_instance(db, instance_id, instance_update)


@router.get("/instances/{instance_id}", response_model=InstanceRead)
def get_instance(instance_id: int, db: Session = Depends(get_db)):
    """
    Retrieve an instance by its ID.

    This endpoint retrieves an instance's details using its unique ID.
    If the instance is not found, a 404 error is returned.

    Parameters:
        - instance_id: The unique ID of the instance to retrieve.
        - db: Database session (injected).

    Returns:
        - The instance's details, including its transformations and associated project/item.

    Raises:
        - 404 HTTPException if the instance is not found.
    """
    return InstanceService.get_instance(db, instance_id)


@router.get("/instances/", response_model=List[InstanceRead])
def list_instances(db: Session = Depends(get_db)):
    """
    List all instances.

    This endpoint retrieves and returns all instances stored in the database.

    Parameters:
        - db: Database session (injected).

    Returns:
        - A list of instances, each containing its transformations and associated project/item.
    """
    return InstanceService.list_instances(db)


@router.delete("/instances/{instance_id}", status_code=204)
def delete_instance(instance_id: int, db: Session = Depends(get_db)):
    """
    Delete an instance by its ID.

    This endpoint deletes an instance using its unique ID.
    If the instance is not found, a 404 error is returned.

    Parameters:
        - instance_id: The unique ID of the instance to delete.
        - db: Database session (injected).

    Returns:
        - A message confirming that the instance has been deleted successfully.

    Raises:
        - 404 HTTPException if the instance is not found.
    """
    return InstanceService.delete_instance(db, instance_id)
