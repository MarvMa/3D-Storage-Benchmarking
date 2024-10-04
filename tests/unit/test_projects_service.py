import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.projects_service import ProjectService


def test_create_project(db_session: Session):
    # Arrange
    project_data = {
        "name": "Test Project",
        "description": "A test project description"
    }

    # Act
    project = ProjectService.create_project(db_session, project_data)

    # Assert
    assert project.name == project_data["name"]
    assert project.description == project_data["description"]
    assert project.qr_code is not None  # QR code should be generated
    assert project.qr_code_url.startswith("http://localhost:8000/projects/")


def test_create_project_failure(db_session: Session):
    # Simulate a failure scenario due to invalid input (missing name and description)
    with pytest.raises(HTTPException) as exc_info:
        project_data = {"name": None, "description": None}  # Invalid data
        ProjectService.create_project(db_session, project_data)

    # Assert that the exception is raised and the correct status code is returned
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Name and description are required fields."


def test_update_project_success(db_session: Session):
    # Arrange
    # First, create a project
    initial_project_data = {
        "name": "Initial Project",
        "description": "Initial description"
    }
    project = ProjectService.create_project(db_session, initial_project_data)

    # New data for the update
    updated_project_data = {
        "name": "Updated Project",
        "description": "Updated description"
    }

    # Act
    updated_project = ProjectService.update_project(db_session, project.id, updated_project_data)

    # Assert
    assert updated_project.name == updated_project_data["name"]
    assert updated_project.description == updated_project_data["description"]
    assert updated_project.qr_code is not None  # QR code should still exist
    assert updated_project.qr_code_url.startswith("http://localhost:8000/projects/")


def test_update_project_not_found(db_session: Session):
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        updated_project_data = {
            "name": "Non-existent Project",
            "description": "Doesn't matter"
        }
        ProjectService.update_project(db_session, 9999, updated_project_data)  # Invalid ID

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Project not found"


def test_get_project_qr_code_success(db_session: Session):
    # Arrange
    project_data = {
        "name": "QR Project",
        "description": "Project for QR code test"
    }
    project = ProjectService.create_project(db_session, project_data)

    # Act
    qr_code = ProjectService.get_project_qr_code(db_session, project.id)

    # Assert
    assert qr_code is not None  # Ensure QR code binary data is returned
    assert project.qr_code_url.startswith("http://localhost:8000/projects/")


def test_get_project_qr_code_not_found(db_session: Session):
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        ProjectService.get_project_qr_code(db_session, 9999)  # Non-existent project ID

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "QR code not found for this project"


def test_get_project_success(db_session: Session):
    # Arrange
    project_data = {
        "name": "Test Project",
        "description": "Project for testing retrieval"
    }
    project = ProjectService.create_project(db_session, project_data)

    # Act
    retrieved_project = ProjectService.get_project(db_session, project.id)

    # Assert
    assert retrieved_project.id == project.id
    assert retrieved_project.name == project_data['name']
    assert retrieved_project.description == project_data['description']
    assert retrieved_project.qr_code_url.startswith("http://localhost:8000/projects/")


def test_get_project_not_found(db_session: Session):
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        ProjectService.get_project(db_session, 9999)  # Non-existent project ID

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Project not found"


def test_list_projects(db_session: Session):
    # Arrange
    project1 = {"name": "Project 1", "description": "Description 1"}
    project2 = {"name": "Project 2", "description": "Description 2"}
    ProjectService.create_project(db_session, project1)
    ProjectService.create_project(db_session, project2)

    # Act
    projects = ProjectService.list_projects(db_session)

    # Assert
    assert len(projects) >= 2
    assert any(
        p.name == project1['name'] and p.qr_code_url.startswith("http://localhost:8000/projects/") for p in projects)
    assert any(
        p.name == project2['name'] and p.qr_code_url.startswith("http://localhost:8000/projects/") for p in projects)


def test_delete_project_success(db_session: Session):
    # Arrange
    project_data = {"name": "Project to delete", "description": "To be deleted"}
    project = ProjectService.create_project(db_session, project_data)

    # Act
    result = ProjectService.delete_project(db_session, project.id)

    # Assert
    assert result['message'] == "Project deleted successfully"

    # Verify deletion
    with pytest.raises(HTTPException) as exc_info:
        ProjectService.get_project(db_session, project.id)
    assert exc_info.value.status_code == 404

    # QR code URL should be valid before deletion
    assert project.qr_code_url.startswith("http://localhost:8000/projects/")


def test_delete_project_not_found(db_session: Session):
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        ProjectService.delete_project(db_session, 9999)  # Non-existent project ID

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Project not found"
