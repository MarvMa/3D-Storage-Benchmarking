from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import Response

from app.services.projects_service import ProjectService
from app.schemas import ProjectCreate, ProjectRead
from app.models import get_db

router = APIRouter()


@router.post("/projects/", response_model=ProjectRead)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """
    Create a new project.

    This endpoint allows users to create a new project with the provided name and description. A QR code will be generated and stored in the database for the project.

    Parameters:
        - project: The project details (name and description).
        - db: Database session (injected).

    Returns:
        - The newly created project with its QR code URL.
    """
    return ProjectService.create_project(db, project)


@router.put("/projects/{project_id}", response_model=ProjectRead)
def update_project(
        project_id: int,
        project_update: ProjectCreate,
        db: Session = Depends(get_db)
):
    """
    Update an existing project.

    This endpoint allows users to update the name and description of an existing project.
    Optionally, the QR code will be regenerated if the project name or description is changed.

    Parameters:
        - project_id: The unique ID of the project to be updated.
        - project_update: The updated project details (name and description).
        - db: Database session (injected).

    Returns:
        - The updated project details, including its QR code URL.

    Raises:
        - 404 HTTPException if the project is not found.
    """
    return ProjectService.update_project(db, project_id, project_update)


@router.get("/projects/{project_id}/qr", response_class=Response)
def get_project_qr_code(project_id: int, db: Session = Depends(get_db)):
    """
    Retrieve the QR code of a project.

    This endpoint allows users to retrieve the QR code for a specific project by its ID.

    Parameters:
        - project_id: The unique ID of the project.
        - db: Database session (injected).

    Returns:
        - The QR code of the project as a PNG image.

    Raises:
        - 404 HTTPException if the project or QR code is not found.
    """
    qr_code = ProjectService.get_project_qr_code(db, project_id)
    return Response(content=qr_code, media_type="image/png")


@router.get("/projects/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """
    Retrieve project details by ID.

    This endpoint allows users to retrieve the details of a project based on its ID.

    Parameters:
        - project_id: The unique ID of the project.
        - db: Database session (injected).

    Returns:
        - The details of the project including its name, description, and QR code URL.

    Raises:
        - 404 HTTPException if the project is not found.
    """
    return ProjectService.get_project(db, project_id)


@router.get("/projects/", response_model=List[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    """
    Retrieve a list of all projects.

    This endpoint allows users to retrieve a list of all projects stored in the database.

    Parameters:
        - db: Database session (injected).

    Returns:
        - A list of all projects including their name, description, and QR code URL.
    """
    return ProjectService.list_projects(db)


@router.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """
    Delete a project by its ID.

    This endpoint allows users to delete a project from the database using its unique ID.

    Parameters:
        - project_id: The unique ID of the project to delete.
        - db: Database session (injected).

    Returns:
        - A message confirming that the project has been successfully deleted.

    Raises:
        - 404 HTTPException if the project is not found
    """
    return ProjectService.delete_project(db, project_id)
