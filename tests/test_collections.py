from app.models import Collection


def test_create_collection(client_with_db):
    """
    Test creating a new collection using the /collections/ POST endpoint.
    """
    response = client_with_db.post(
        "/collections/",
        json={"name": "Test Collection", "description": "Test Collection Description"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["name"] == "Test Collection"
    assert json_data["description"] == "Test Collection Description"
    assert "id" in json_data


def test_create_collection_invalid_payload(client_with_db):
    """
    Test creating a collection with invalid data to ensure it handles errors properly.
    """
    response = client_with_db.post(
        "/collections/",
        json={"name": ""}
    )
    assert response.status_code == 422  # Validation error


def test_update_collection(client_with_db, db_session):
    """
    Test updating a collection using the /collections/{collection_id} PUT endpoint.
    """
    # Create a collection in the test database
    collection = Collection(name="Original Collection", description="Original Description")
    db_session.add(collection)
    db_session.commit()

    # Update the collection
    update_data = {"name": "Updated Collection", "description": "Updated Description"}
    response = client_with_db.put(f"/collections/{collection.id}", json=update_data)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["name"] == "Updated Collection"
    assert json_data["description"] == "Updated Description"

    # Fetch the updated collection to verify
    response = client_with_db.get(f"/collections/{collection.id}")
    assert response.status_code == 200
    fetched_collection = response.json()
    assert fetched_collection["name"] == "Updated Collection"
    assert fetched_collection["description"] == "Updated Description"


def test_update_collection_not_found(client_with_db):
    """
    Test updating a collection that does not exist to ensure proper error handling.
    """
    update_data = {"name": "Non-existent Collection", "description": "This won't work"}
    response = client_with_db.put("/collections/99999", json=update_data)  # Use a non-existent ID
    assert response.status_code == 404
    assert response.json()["detail"] == "Collection not found"


def test_get_collection(client_with_db, db_session):
    """
    Test retrieving a collection using the /collections/{collection_id} GET endpoint.
    """
    # Create a collection in the test database
    collection = Collection(name="Test Collection 2", description="Another Test Collection")
    db_session.add(collection)
    db_session.commit()

    # Retrieve the collection by ID
    response = client_with_db.get(f"/collections/{collection.id}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["name"] == "Test Collection 2"
    assert json_data["description"] == "Another Test Collection"


def test_get_collection_not_found(client_with_db):
    """
    Test retrieving a collection that does not exist to ensure proper error handling.
    """
    response = client_with_db.get("/collections/99999")  # Use a non-existent ID
    assert response.status_code == 404
    assert response.json()["detail"] == "Collection not found"


def test_list_collections(client_with_db, db_session):
    """
    Test listing all collections using the /collections/ GET endpoint.
    """
    # Create multiple collections in the test database
    collection1 = Collection(name="Test Collection 3", description="Test Collection Description 3")
    collection2 = Collection(name="Test Collection 4", description="Test Collection Description 4")
    db_session.add_all([collection1, collection2])
    db_session.commit()

    # Retrieve all collections
    response = client_with_db.get("/collections/")
    assert response.status_code == 200
    json_data = response.json()
    assert len(json_data) >= 2
    assert json_data[0]["name"] == "Test Collection 3"
    assert json_data[1]["name"] == "Test Collection 4"


def test_delete_collection(client_with_db, db_session):
    """
    Test deleting a collection using the /collections/{collection_id} DELETE endpoint.
    """
    # Create a collection in the test database
    collection = Collection(name="Test Collection 5", description="Test Collection for Deletion")
    db_session.add(collection)
    db_session.commit()

    # Delete the collection
    response = client_with_db.delete(f"/collections/{collection.id}")
    assert response.status_code == 204

    # Verify the collection no longer exists
    response = client_with_db.get(f"/collections/{collection.id}")
    assert response.status_code == 404


def test_delete_collection_not_found(client_with_db):
    """
    Test deleting a collection that does not exist to ensure proper error handling.
    """
    response = client_with_db.delete("/collections/99999")  # Use a non-existent ID
    assert response.status_code == 404
    assert response.json()["detail"] == "Collection not found"
