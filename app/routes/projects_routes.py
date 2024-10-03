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
        Create a new project.

        This endpoint allows users to create a new project with the provided name and description. A QR code will be generated and stored in the database for the project.

        Parameters:
            - project: The project details (name and description).
            - db: Database session (injected).

        Returns:
            - The newly created project with its QR code URL.
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
    new_project.qr_code_url = project_url

    db.commit()

    # Return the project with the QR code URL
    return new_project


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
    # Retrieve the project from the database
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    # Update the project's name and description
    project.name = project_update.name
    project.description = project_update.description

    # Regenerate the QR code if necessary
    project_url = f"http://localhost:8000/projects/{project.id}/qr"
    qr = qrcode.make(project_url)
    qr_bytes = BytesIO()
    qr.save(qr_bytes, format="PNG")
    project.qr_code = qr_bytes.getvalue()
    project.qr_code_url = project_url

    # Commit the changes to the database
    db.commit()
    db.refresh(project)

    return project


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
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None or project.qr_code is None:
        raise HTTPException(status_code=404, detail="QR code not found for this project")

    return Response(content=project.qr_code, media_type="image/png")


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

        This endpoint allows users to retrieve a list of all projects stored in the database.

        Parameters:
            - db: Database session (injected).

        Returns:
            - A list of all projects including their name, description, and QR code URL.
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
    Retrieve a list of all projects.

    This endpoint allows users to retrieve a list of all projects stored in the database.

    Parameters:
        - db: Database session (injected).

    Returns:
        - A list of all projects including their name, description, and QR code URL.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}
