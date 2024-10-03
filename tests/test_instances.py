from app.models import Project, Item, Instance


def test_create_instance(client_with_db, db_session):
    """
    Test creating a new instance via the /instances/ POST endpoint.
    """
    # Create a project and an item in the test database
    project = Project(name="Test Project", description="Test Project Description")
    item = Item(name="Test Item", description="Test Item Description", file_path="test.gltf")
    db_session.add_all([project, item])
    db_session.commit()

    # Create an instance
    response = client_with_db.post(
        "/instances/",
        json={
            "project_id": project.id,
            "item_id": item.id,
            "position_x": 1.0,
            "position_y": 1.0,
            "position_z": 1.0,
            "rotation_x": 0.0,
            "rotation_y": 0.0,
            "rotation_z": 0.0,
            "scale_x": 1.0,
            "scale_y": 1.0,
            "scale_z": 1.0
        }
    )
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["project_id"] == project.id
    assert json_data["item_id"] == item.id


def test_create_instance_project_not_found(client_with_db, db_session):
    """
    Test creating an instance with a non-existent project via the /instances/ POST endpoint.
    """
    # Create an item in the test database
    item = Item(name="Test Item", description="Test Item Description", file_path="test.gltf")
    db_session.add(item)
    db_session.commit()

    # Try to create an instance with a non-existent project
    response = client_with_db.post(
        "/instances/",
        json={
            "project_id": 9999,  # Non-existent project
            "item_id": item.id,
            "position_x": 1.0,
            "position_y": 1.0,
            "position_z": 1.0,
            "rotation_x": 0.0,
            "rotation_y": 0.0,
            "rotation_z": 0.0,
            "scale_x": 1.0,
            "scale_y": 1.0,
            "scale_z": 1.0
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_create_instance_item_not_found(client_with_db, db_session):
    """
    Test creating an instance with a non-existent item via the /instances/ POST endpoint.
    """
    # Create a project in the test database
    project = Project(name="Test Project", description="Test Project Description")
    db_session.add(project)
    db_session.commit()

    # Try to create an instance with a non-existent item
    response = client_with_db.post(
        "/instances/",
        json={
            "project_id": project.id,
            "item_id": 9999,  # Non-existent item
            "position_x": 1.0,
            "position_y": 1.0,
            "position_z": 1.0,
            "rotation_x": 0.0,
            "rotation_y": 0.0,
            "rotation_z": 0.0,
            "scale_x": 1.0,
            "scale_y": 1.0,
            "scale_z": 1.0
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_update_instance(client_with_db, db_session):
    """
    Test updating an instance via the /instances/{instance_id} PUT endpoint.
    """
    # Create a project, item, and instance in the test database
    project = Project(name="Test Project", description="Test Project Description")
    item = Item(name="Test Item", description="Test Item Description", file_path="test.gltf")
    db_session.add_all([project, item])
    db_session.commit()

    instance = Instance(
        project_id=project.id, item_id=item.id,
        position_x=1.0, position_y=1.0, position_z=1.0,
        rotation_x=0.0, rotation_y=0.0, rotation_z=0.0,
        scale_x=1.0, scale_y=1.0, scale_z=1.0
    )
    db_session.add(instance)
    db_session.commit()

    # Update the instance
    updated_data = {
        "project_id": project.id,
        "item_id": item.id,
        "position_x": 2.0,
        "position_y": 2.0,
        "position_z": 2.0,
        "rotation_x": 1.0,
        "rotation_y": 1.0,
        "rotation_z": 1.0,
        "scale_x": 2.0,
        "scale_y": 2.0,
        "scale_z": 2.0
    }
    response = client_with_db.put(f"/instances/{instance.id}", json=updated_data)
    assert response.status_code == 200
    json_data = response.json()

    # Verify the updated fields
    assert json_data["position_x"] == 2.0
    assert json_data["position_y"] == 2.0
    assert json_data["position_z"] == 2.0
    assert json_data["rotation_x"] == 1.0
    assert json_data["rotation_y"] == 1.0
    assert json_data["rotation_z"] == 1.0
    assert json_data["scale_x"] == 2.0
    assert json_data["scale_y"] == 2.0
    assert json_data["scale_z"] == 2.0


def test_update_instance_not_found(client_with_db):
    """
    Test updating a non-existent instance via the /instances/{instance_id} PUT endpoint.
    """
    updated_data = {
        "project_id": 9999,  # Non-existent project
        "item_id": 9999,  # Non-existent item
        "position_x": 2.0,
        "position_y": 2.0,
        "position_z": 2.0,
        "rotation_x": 1.0,
        "rotation_y": 1.0,
        "rotation_z": 1.0,
        "scale_x": 2.0,
        "scale_y": 2.0,
        "scale_z": 2.0
    }
    response = client_with_db.put("/instances/9999", json=updated_data)  # Non-existent instance
    assert response.status_code == 404
    assert response.json()["detail"] == "Instance not found"


def test_update_instance_project_not_found(client_with_db, db_session):
    """
    Test updating an instance with a non-existent project via the /instances/{instance_id} PUT endpoint.
    """
    # Create an item and instance in the test database
    item = Item(name="Test Item", description="Test Item Description", file_path="test.gltf")
    db_session.add(item)
    db_session.commit()

    instance = Instance(
        project_id=1,  # Assuming project with ID 1 doesn't exist
        item_id=item.id,
        position_x=1.0, position_y=1.0, position_z=1.0,
        rotation_x=0.0, rotation_y=0.0, rotation_z=0.0,
        scale_x=1.0, scale_y=1.0, scale_z=1.0
    )
    db_session.add(instance)
    db_session.commit()

    # Try to update the instance with a non-existent project
    updated_data = {
        "project_id": 9999,  # Non-existent project
        "item_id": item.id,
        "position_x": 2.0,
        "position_y": 2.0,
        "position_z": 2.0,
        "rotation_x": 1.0,
        "rotation_y": 1.0,
        "rotation_z": 1.0,
        "scale_x": 2.0,
        "scale_y": 2.0,
        "scale_z": 2.0
    }
    response = client_with_db.put(f"/instances/{instance.id}", json=updated_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


def test_update_instance_item_not_found(client_with_db, db_session):
    """
    Test updating an instance with a non-existent item via the /instances/{instance_id} PUT endpoint.
    """
    # Create a project and instance in the test database
    project = Project(name="Test Project", description="Test Project Description")
    db_session.add(project)
    db_session.commit()

    instance = Instance(
        project_id=project.id,
        item_id=1,  # Assuming item with ID 1 doesn't exist
        position_x=1.0, position_y=1.0, position_z=1.0,
        rotation_x=0.0, rotation_y=0.0, rotation_z=0.0,
        scale_x=1.0, scale_y=1.0, scale_z=1.0
    )
    db_session.add(instance)
    db_session.commit()

    # Try to update the instance with a non-existent item
    updated_data = {
        "project_id": project.id,
        "item_id": 9999,  # Non-existent item
        "position_x": 2.0,
        "position_y": 2.0,
        "position_z": 2.0,
        "rotation_x": 1.0,
        "rotation_y": 1.0,
        "rotation_z": 1.0,
        "scale_x": 2.0,
        "scale_y": 2.0,
        "scale_z": 2.0
    }
    response = client_with_db.put(f"/instances/{instance.id}", json=updated_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_get_instance(client_with_db, db_session):
    """
    Test retrieving an instance by ID via the /instances/{instance_id} GET endpoint.
    """
    # Create a project and item in the test database
    project = Project(name="Test Project", description="Test Project Description")
    item = Item(name="Test Item", description="Test Item Description", file_path="test.gltf")
    db_session.add_all([project, item])
    db_session.commit()

    # Create an instance
    instance = Instance(
        project_id=project.id,
        item_id=item.id,
        position_x=1.0,
        position_y=1.0,
        position_z=1.0,
        rotation_x=0.0,
        rotation_y=0.0,
        rotation_z=0.0,
        scale_x=1.0,
        scale_y=1.0,
        scale_z=1.0
    )
    db_session.add(instance)
    db_session.commit()

    # Retrieve the instance by ID
    response = client_with_db.get(f"/instances/{instance.id}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["project_id"] == project.id
    assert json_data["item_id"] == item.id


def test_get_instance_not_found(client_with_db):
    """
    Test retrieving a non-existent instance by ID via the /instances/{instance_id} GET endpoint.
    """
    response = client_with_db.get("/instances/9999")  # Non-existent instance
    assert response.status_code == 404
    assert response.json()["detail"] == "Instance not found"


def test_list_instances(client_with_db, db_session):
    """
    Test listing all instances via the /instances/ GET endpoint.
    """
    # Create a project, item, and instances in the test database
    project = Project(name="Test Project", description="Test Project Description")
    item = Item(name="Test Item", description="Test Item Description", file_path="test.gltf")
    db_session.add_all([project, item])
    db_session.commit()

    # Create two instances
    instance1 = Instance(
        project_id=project.id, item_id=item.id,
        position_x=1.0, position_y=1.0, position_z=1.0,
        rotation_x=0.0, rotation_y=0.0, rotation_z=0.0,
        scale_x=1.0, scale_y=1.0, scale_z=1.0
    )
    instance2 = Instance(
        project_id=project.id, item_id=item.id,
        position_x=2.0, position_y=2.0, position_z=2.0,
        rotation_x=1.0, rotation_y=1.0, rotation_z=1.0,
        scale_x=2.0, scale_y=2.0, scale_z=2.0
    )
    db_session.add_all([instance1, instance2])
    db_session.commit()

    # Retrieve the list of instances
    response = client_with_db.get("/instances/")
    assert response.status_code == 200
    json_data = response.json()
    assert len(json_data) >= 2
    assert json_data[0]["project_id"] == project.id
    assert json_data[0]["item_id"] == item.id
    assert json_data[1]["project_id"] == project.id
    assert json_data[1]["item_id"] == item.id


def test_delete_instance(client_with_db, db_session):
    """
    Test deleting an instance by ID via the /instances/{instance_id} DELETE endpoint.
    """
    # Create a project, item, and instance in the test database
    project = Project(name="Test Project", description="Test Project Description")
    item = Item(name="Test Item", description="Test Item Description", file_path="test.gltf")
    instance = Instance(
        project_id=project.id, item_id=item.id,
        position_x=1.0, position_y=1.0, position_z=1.0,
        rotation_x=0.0, rotation_y=0.0, rotation_z=0.0,
        scale_x=1.0, scale_y=1.0, scale_z=1.0
    )
    db_session.add_all([project, item, instance])
    db_session.commit()

    # Delete the instance by ID
    response = client_with_db.delete(f"/instances/{instance.id}")
    assert response.status_code == 204

    # Verify the instance was deleted
    response = client_with_db.get(f"/instances/{instance.id}")
    assert response.status_code == 404


def test_delete_instance_not_found(client_with_db):
    """
    Test trying to delete a non-existent instance by ID via the /instances/{instance_id} DELETE endpoint.
    """
    response = client_with_db.delete("/instances/9999")  # Non-existent instance
    assert response.status_code == 404
    assert response.json()["detail"] == "Instance not found"
