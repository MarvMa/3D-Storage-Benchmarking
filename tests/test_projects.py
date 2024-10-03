from app.models import Project


def test_create_project(client_with_db):
    """
    Test creating a new project with QR code using the /projects/ POST endpoint.
    """
    response = client_with_db.post(
        "/projects/",
        json={"name": "Test Project", "description": "Test Project Description"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["name"] == "Test Project"
    assert json_data["description"] == "Test Project Description"
    assert "qr_code_url" in json_data


def test_get_project(client_with_db, db_session):
    """
    Test retrieving a project by ID using the /projects/{project_id} GET endpoint.
    """
    # Create a project in the test database
    project = Project(name="Test Project 2", description="Another Test Project")
    db_session.add(project)
    db_session.commit()

    # Retrieve the project by ID
    response = client_with_db.get(f"/projects/{project.id}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["name"] == "Test Project 2"
    assert json_data["description"] == "Another Test Project"


def test_get_project_not_found(client_with_db):
    """
    Test retrieving a non-existent project by ID to trigger a 404 error.
    """
    response = client_with_db.get("/projects/9999")
    assert response.status_code == 404
    json_data = response.json()
    assert json_data["detail"] == "Project not found"


def test_get_project_qr_code(client_with_db, db_session):
    """
    Test retrieving a project's QR code using the /projects/{project_id}/qr GET endpoint.
    """
    # Create a project in the test database
    response = client_with_db.post(
        "/projects/",
        json={"name": "Test Project QR", "description": "Project With QR"}
    )
    assert response.status_code == 200
    project_id = response.json()["id"]

    # Retrieve the project's QR code by ID
    response = client_with_db.get(f"/projects/{project_id}/qr")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


def test_get_project_qr_code_not_found(client_with_db):
    """
    Test retrieving a non-existent project's QR code to trigger a 404 error.
    """
    response = client_with_db.get("/projects/9999/qr")
    assert response.status_code == 404
    json_data = response.json()
    assert json_data["detail"] == "QR code not found for this project"


def test_list_projects(client_with_db, db_session):
    """
    Test listing all projects using the /projects/ GET endpoint.
    """
    # Create multiple projects in the test database
    project1 = Project(name="Test Project 4", description="Project 4 Description")
    project2 = Project(name="Test Project 5", description="Project 5 Description")
    db_session.add_all([project1, project2])
    db_session.commit()

    # Retrieve the list of all projects
    response = client_with_db.get("/projects/")
    assert response.status_code == 200
    json_data = response.json()
    assert len(json_data) >= 2
    assert json_data[0]["name"] == "Test Project 4"
    assert json_data[1]["name"] == "Test Project 5"


def test_delete_project(client_with_db, db_session):
    """
    Test deleting a project by ID using the /projects/{project_id} DELETE endpoint.
    """
    # Create a project in the test database
    project = Project(name="Test Project 6", description="Test Project for Deletion")
    db_session.add(project)
    db_session.commit()

    # Delete the project by ID
    response = client_with_db.delete(f"/projects/{project.id}")
    assert response.status_code == 204

    # Verify the project no longer exists
    response = client_with_db.get(f"/projects/{project.id}")
    assert response.status_code == 404


def test_delete_project_not_found(client_with_db):
    """
    Test deleting a non-existent project to trigger a 404 error.
    """
    response = client_with_db.delete("/projects/9999")
    assert response.status_code == 404
    json_data = response.json()
    assert json_data["detail"] == "Project not found"
