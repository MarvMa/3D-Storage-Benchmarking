from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Instance, Project, Item
from app.services.instances_service import InstanceService


def test_create_instance_success(db_session: Session):
    # Arrange
    project = Project(id=1, name="Test Project")
    item = Item(id=1, name="Test Item")

    with patch.object(db_session, 'query', return_value=MagicMock(
            filter=MagicMock(return_value=MagicMock(first=MagicMock(side_effect=[project, item]))))):
        instance_data = MagicMock()
        instance_data.project_id = 1
        instance_data.item_id = 1
        instance_data.position_x = 0.0
        instance_data.position_y = 0.0
        instance_data.position_z = 0.0
        instance_data.rotation_x = 0.0
        instance_data.rotation_y = 0.0
        instance_data.rotation_z = 0.0
        instance_data.scale_x = 1.0
        instance_data.scale_y = 1.0
        instance_data.scale_z = 1.0

        # Act
        instance = InstanceService.create_instance(db_session, instance_data)

        # Assert
        assert instance.project_id == instance_data.project_id
        assert instance.item_id == instance_data.item_id
        assert instance.position_x == instance_data.position_x


def test_create_instance_project_not_found(db_session: Session):
    with patch.object(db_session, 'query', return_value=MagicMock(
            filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None))))):
        instance_data = MagicMock()
        instance_data.project_id = 1
        instance_data.item_id = 1

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            InstanceService.create_instance(db_session, instance_data)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Project not found"


def test_update_instance_success(db_session: Session):
    # Arrange
    project = Project(id=1, name="Test Project")
    item = Item(id=1, name="Test Item")
    instance = Instance(id=1, project_id=1, item_id=1, position_x=0.0, position_y=0.0, position_z=0.0)

    with patch.object(db_session, 'query', return_value=MagicMock(
            filter=MagicMock(return_value=MagicMock(first=MagicMock(side_effect=[instance, project, item]))))):
        updated_data = MagicMock()
        updated_data.project_id = 1
        updated_data.item_id = 1
        updated_data.position_x = 1.0
        updated_data.position_y = 1.0
        updated_data.position_z = 1.0

        # Act
        with patch.object(db_session, 'refresh', return_value=None):  # Mock db.refresh
            updated_instance = InstanceService.update_instance(db_session, instance.id, updated_data)

        # Assert
        assert updated_instance.position_x == updated_data.position_x
        assert updated_instance.position_y == updated_data.position_y
        assert updated_instance.position_z == updated_data.position_z


def test_update_instance_not_found(db_session: Session):
    with patch.object(db_session, 'query', return_value=MagicMock(
            filter=MagicMock(return_value=MagicMock(first=MagicMock(side_effect=[None]))))):
        updated_data = MagicMock()

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            InstanceService.update_instance(db_session, 9999, updated_data)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Instance not found"


def test_get_instance_success(db_session: Session):
    # Arrange
    instance = Instance(id=1, project_id=1, item_id=1, position_x=0.0, position_y=0.0, position_z=0.0)

    with patch.object(db_session, 'query', return_value=MagicMock(
            filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=instance))))):
        # Act
        retrieved_instance = InstanceService.get_instance(db_session, instance.id)

        # Assert
        assert retrieved_instance.id == instance.id
        assert retrieved_instance.project_id == instance.project_id
        assert retrieved_instance.item_id == instance.item_id


def test_get_instance_not_found(db_session: Session):
    with patch.object(db_session, 'query', return_value=MagicMock(
            filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None))))):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            InstanceService.get_instance(db_session, 9999)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Instance not found"


def test_list_instances_success(db_session: Session):
    # Arrange
    instance1 = Instance(id=1, project_id=1, item_id=1, position_x=0.0, position_y=0.0, position_z=0.0)
    instance2 = Instance(id=2, project_id=1, item_id=2, position_x=1.0, position_y=1.0, position_z=1.0)

    with patch.object(db_session, 'query', return_value=MagicMock(all=MagicMock(return_value=[instance1, instance2]))):
        # Act
        instances = InstanceService.list_instances(db_session)

        # Assert
        assert len(instances) == 2
        assert instances[0].id == instance1.id
        assert instances[1].id == instance2.id


def test_delete_instance_success(db_session: Session):
    # Arrange
    instance = Instance(id=1, project_id=1, item_id=1, position_x=0.0, position_y=0.0, position_z=0.0)

    with patch.object(db_session, 'query', return_value=MagicMock(
            filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=instance))))):
        # Act
        with patch.object(db_session, 'delete', return_value=None):  # Mock db.delete
            result = InstanceService.delete_instance(db_session, instance.id)

        # Assert
        assert result["message"] == "Instance deleted successfully"


def test_delete_instance_not_found(db_session: Session):
    with patch.object(db_session, 'query', return_value=MagicMock(
            filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None))))):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            InstanceService.delete_instance(db_session, 9999)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Instance not found"
