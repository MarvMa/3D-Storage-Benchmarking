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
    # Create the new project
    new_project = Project(name=project.name, description=project.description)
    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    # Generate QR code URL
    project_url = f"http://localhost:8000/projects/{new_project.id}/qr"

    # Generate and store the QR code as binary data
    qr = qrcode.make(project_url)
    qr_bytes = BytesIO()
    qr.save(qr_bytes, format="PNG")
    new_project.qr_code = qr_bytes.getvalue()
    new_project.qr_code_url = project_url  # Store the QR code URL in the database

    db.commit()

    # Return the project with the QR code URL
    return new_project


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

    # Generate the qr_code_url if it is missing
    if project.qr_code_url is None:
        project.qr_code_url = f"http://localhost:8000/projects/{project.id}/qr"
        db.commit()  # Save the updated QR code URL in the database

    return project


@router.get("/projects/", response_model=List[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    """
    Retrieve a list of all projects.
    """
    projects = db.query(Project).all()

    # Ensure all projects have a qr_code_url
    for project in projects:
        if project.qr_code_url is None:
            project.qr_code_url = f"http://localhost:8000/projects/{project.id}/qr"
            db.commit()

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
