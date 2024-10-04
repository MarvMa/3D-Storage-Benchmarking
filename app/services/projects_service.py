from io import BytesIO

import qrcode
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Project


class ProjectService:
    """
    Service layer for managing projects and their QR codes.

    This class provides methods for creating, updating, retrieving, and deleting projects,
    as well as generating and retrieving QR codes for the projects.
    """

    @staticmethod
    def create_project(db: Session, project_data: dict):
        """
        Create a new project and generate a QR code for it.

        Parameters:
            - db: Database session.
            - project_data: The project details including name and description (as a dict).

        Returns:
            - The newly created project with its QR code URL.

        Raises:
            - HTTPException with status code 400 if name or description are invalid.
            - HTTPException with status code 500 if QR code generation fails.
        """
        # Validate input
        if not project_data.get('name') or not project_data.get('description'):
            raise HTTPException(status_code=400, detail="Name and description are required fields.")

        new_project = Project(name=project_data['name'], description=project_data['description'])
        db.add(new_project)
        db.commit()
        db.refresh(new_project)

        # Generate QR code URL
        project_url = f"http://localhost:8000/projects/{new_project.id}/qr"

        # Generate and store the QR code as binary data
        try:
            qr = qrcode.make(project_url)
            qr_bytes = BytesIO()
            qr.save(qr_bytes, format="PNG")
            new_project.qr_code = qr_bytes.getvalue()
            new_project.qr_code_url = project_url
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to generate QR code.")

        db.commit()
        return new_project

    @staticmethod
    def update_project(db: Session, project_id: int, project_data: dict):
        """
        Update an existing project and regenerate the QR code if necessary.

        Parameters:
            - db: Database session.
            - project_id: The unique ID of the project to update.
            - project_data: The updated project details including name and description (as a dict).

        Returns:
            - The updated project details, including its QR code URL.

        Raises:
            - HTTPException with status code 404 if the project is not found.
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        # Update the project's name and description
        project.name = project_data['name']
        project.description = project_data['description']

        # Regenerate the QR code
        project_url = f"http://localhost:8000/projects/{project.id}/qr"
        qr = qrcode.make(project_url)
        qr_bytes = BytesIO()
        qr.save(qr_bytes, format="PNG")
        project.qr_code = qr_bytes.getvalue()
        project.qr_code_url = project_url

        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get_project_qr_code(db: Session, project_id: int):
        """
        Retrieve the QR code of a project by its ID.

        Parameters:
            - db: Database session.
            - project_id: The unique ID of the project.

        Returns:
            - The QR code as binary data.

        Raises:
            - HTTPException with status code 404 if the project or its QR code is not found.
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None or project.qr_code is None:
            raise HTTPException(status_code=404, detail="QR code not found for this project")

        return project.qr_code

    @staticmethod
    def get_project(db: Session, project_id: int):
        """
        Retrieve the details of a project by its ID.

        Parameters:
            - db: Database session.
            - project_id: The unique ID of the project to retrieve.

        Returns:
            - The project details, including its name, description, and QR code URL.

        Raises:
            - HTTPException with status code 404 if the project is not found.
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        # Ensure the QR code URL is set
        if project.qr_code_url is None:
            project.qr_code_url = f"http://localhost:8000/projects/{project.id}/qr"
            db.commit()

        return project

    @staticmethod
    def list_projects(db: Session):
        """
        Retrieve a list of all projects.

        Parameters:
            - db: Database session.

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

    @staticmethod
    def delete_project(db: Session, project_id: int):
        """
        Delete a project by its ID.

        Parameters:
            - db: Database session.
            - project_id: The unique ID of the project to delete.

        Returns:
            - A message confirming that the project has been deleted successfully.

        Raises:
            - HTTPException with status code 404 if the project is not found.
        """
        project = db.query(Project).filter(Project.id == project_id).first()
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        db.delete(project)
        db.commit()
        return {"message": "Project deleted successfully"}
