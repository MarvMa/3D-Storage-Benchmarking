from app.models import Item


def test_create_item(client_with_db):
    """
    Test the /items/ POST endpoint
    """
    response = client_with_db.post(
        "/items/",
        data={"name": "Test Item", "description": "Test Description"},
        files={"file": ("test.gltf", b"Some Gltf File Content", "application/octet-stream")},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Item"


def test_create_item_missing_file(client_with_db):
    """
    Test the /items/ POST endpoint with a missing file to trigger a 422 error.
    """
    response = client_with_db.post(
        "/items/",
        data={"name": "Test Item", "description": "Test Description"}
    )
    assert response.status_code == 422  # Unprocessable Entity (file is required)


def test_read_item(client_with_db):
    """
    Test the /items/{item_id} GET endpoint
    """
    # Create an item
    response = client_with_db.post(
        "/items/",
        data={"name": "Test Item Read", "description": "Test Description"},
        files={"file": ("test.gltf", b"Some Gltf File Content", "application/octet-stream")},
    )
    assert response.status_code == 200
    item_id = response.json()["id"]

    # Get the item
    response = client_with_db.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Item Read"


def test_read_item_not_found(client_with_db):
    """
    Test the /items/{item_id} GET endpoint with a non-existent item to trigger a 404 error.
    """
    response = client_with_db.get("/items/9999")
    assert response.status_code == 404  # Item not found
    assert response.json()["detail"] == "Item not found"


def test_download_item(client_with_db):
    """
    Test the /items/{item_id}/download GET endpoint
    """
    # Create an item
    response = client_with_db.post(
        "/items/",
        data={"name": "Test Item Download", "description": "Test Description"},
        files={"file": ("test.gltf", b"Some Gltf File Content", "application/octet-stream")},
    )
    assert response.status_code == 200
    item_id = response.json()["id"]

    # Download the file
    response = client_with_db.get(f"/items/{item_id}/download")
    assert response.status_code == 200
    assert response.headers["content-disposition"].startswith("attachment")
    assert response.content == b"Some Gltf File Content"  # Check the file content


def test_download_item_not_found(client_with_db):
    """
    Test the /items/{item_id}/download GET endpoint with a non-existent item to trigger a 404 error.
    """
    response = client_with_db.get("/items/9999/download")
    assert response.status_code == 404  # Item not found
    assert response.json()["detail"] == "Item not found"


def test_download_file_not_found_on_server(client_with_db, db_session):
    """
    Test the /items/{item_id}/download GET endpoint where the item exists but the file is missing on the server.
    """
    # Create an item with a valid path in the database but the file doesn't exist on disk
    item = Item(name="Test Item", description="Test Item", file_path="non_existent_file.gltf")
    db_session.add(item)
    db_session.commit()

    # Try to download the missing file
    response = client_with_db.get(f"/items/{item.id}/download")
    assert response.status_code == 404  # File not found on server
    assert response.json()["detail"] == "File not found on server"


def test_delete_item(client_with_db):
    """
    Test the /items/{item_id} DELETE endpoint
    """
    # Create an item
    response = client_with_db.post(
        "/items/",
        data={"name": "Test Item to Delete", "description": "Test Description"},
        files={"file": ("test.gltf", b"Some Gltf File Content", "application/octet-stream")},
    )
    assert response.status_code == 200
    item_id = response.json()["id"]

    # Delete the item
    response = client_with_db.delete(f"/items/{item_id}")
    assert response.status_code == 204

    # Verify the item is deleted
    response = client_with_db.get(f"/items/{item_id}")
    assert response.status_code == 404  # Item not found


def test_delete_item_not_found(client_with_db):
    """
    Test the /items/{item_id} DELETE endpoint with a non-existent item to trigger a 404 error.
    """
    response = client_with_db.delete("/items/9999")
    assert response.status_code == 404  # Item not found
    assert response.json()["detail"] == "Item not found"


def test_full_item_lifecycle(client_with_db):
    """
    Test the full lifecycle of an item (create, retrieve, delete).
    """
    # Create an item
    response = client_with_db.post(
        "/items/",
        data={"name": "Test Item", "description": "Test Description"},
        files={"file": ("test.gltf", b"Some Gltf File Content", "application/octet-stream")},
    )
    assert response.status_code == 200
    item_id = response.json()["id"]

    # Retrieve the item
    response = client_with_db.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Item"

    # Delete the item
    response = client_with_db.delete(f"/items/{item_id}")
    assert response.status_code == 204

    # Verify the item is deleted
    response = client_with_db.get(f"/items/{item_id}")
    assert response.status_code == 404  # Item not found
