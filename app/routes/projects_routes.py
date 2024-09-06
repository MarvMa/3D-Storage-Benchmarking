from io import BytesIO
from typing import List

import qrcode
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.models import Project, get_db
from app.schemas import ProjectCreate, ProjectRead

router = APIRouter()


@router.post("/projects/", response_model=ProjectRead)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """
    Create a new project with the provided name and description, generate a QR code, and store it in the database.
    """
    new_project = Project(name=project.name, description=project.description)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    project_url = f"http://localhost:8000/projects/{new_project.id}"

    qr = qrcode.make(project_url)
    qr_bytes = BytesIO()
    qr.save(qr_bytes, format="PNG")
    new_project.qr_code = qr_bytes.getvalue()

    db.commit()

    return {
        "id": new_project.id,
        "name": new_project.name,
        "description": new_project.description,
        "qr_code_url": f"http://localhost:8000/projects/{new_project.id}/qr"
    }


@router.get("/projects/{project_id}/qr", response_class=Response)
def get_project_qr_code(project_id: int, db: Session = Depends(get_db)):
    """
    Retrieve the QR code for a specific project by its ID from the database.
    """
    # Projekt aus der Datenbank abrufen
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None or project.qr_code is None:
        raise HTTPException(status_code=404, detail="QR code not found for this project")

    return Response(content=project.qr_code, media_type="image/png")


@router.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a project by its ID.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/projects/", response_model=List[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    """
    Retrieve a list of all projects.
    """
    projects = db.query(Project).all()
    return projects


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
    Delete a project by its ID.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}
