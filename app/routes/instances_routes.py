from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.models import Instance, Project, Item, get_db
from app.schemas import InstanceCreate, InstanceRead

router = APIRouter()


@router.post("/instances/", response_model=InstanceRead)
def create_instance(instance: InstanceCreate, db: Session = Depends(get_db)):
    # Ensure the project and item exist
    project = db.query(Project).filter(Project.id == instance.project_id).first()
    item = db.query(Item).filter(Item.id == instance.item_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # Create and save the new instance
    new_instance = Instance(
        project_id=instance.project_id,
        item_id=instance.item_id,
        position_x=instance.position_x,
        position_y=instance.position_y,
        position_z=instance.position_z,
        rotation_x=instance.rotation_x,
        rotation_y=instance.rotation_y,
        rotation_z=instance.rotation_z,
        scale_x=instance.scale_x,
        scale_y=instance.scale_y,
        scale_z=instance.scale_z
    )
    db.add(new_instance)
    db.commit()
    db.refresh(new_instance)
    return new_instance


@router.get("/instances/{instance_id}", response_model=InstanceRead)
def get_instance(instance_id: int, db: Session = Depends(get_db)):
    instance = db.query(Instance).filter(Instance.id == instance_id).first()
    if instance is None:
        raise HTTPException(status_code=404, detail="Instance not found")
    return instance


@router.get("/instances/", response_model=List[InstanceRead])
def list_instances(db: Session = Depends(get_db)):
    instances = db.query(Instance).all()
    return instances


@router.delete("/instances/{instance_id}", status_code=204)
def delete_instance(instance_id: int, db: Session = Depends(get_db)):
    instance = db.query(Instance).filter(Instance.id == instance_id).first()
    if instance is None:
        raise HTTPException(status_code=404, detail="Instance not found")
    db.delete(instance)
    db.commit()
    return {"message": "Instance deleted successfully"}
