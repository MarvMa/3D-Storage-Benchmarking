from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.item_service import ItemService


def test_create_item_success(db_session: Session):
    # Arrange
    name = "Test Item"
    description = "A test item"
    mock_file = MagicMock()
    mock_file.filename = "testfile.txt"

    # Act
    with patch("shutil.copyfileobj", MagicMock()):
        item = ItemService.create_item(db_session, name, description, mock_file)

    # Assert
    assert item.name == name
    assert item.description == description
    assert item.file_path.endswith("testfile.txt")


def test_create_item_failure(db_session: Session):
    # Arrange
    description = "A test item"
    mock_file = MagicMock()
    mock_file.filename = "testfile.txt"

    # Simulate a failure by setting an empty name
    with patch("shutil.copyfileobj", MagicMock()), \
            pytest.raises(HTTPException) as exc_info:
        ItemService.create_item(db_session, "", description, mock_file)

    assert exc_info.value.status_code == 400


def test_update_item_success(db_session: Session):
    # Arrange
    mock_file = MagicMock()
    mock_file.filename = "oldfile.txt"
    with patch("shutil.copyfileobj", MagicMock()):
        item = ItemService.create_item(db_session, "Old Item", "Old Description", mock_file)

    updated_name = "Updated Item"
    updated_description = "Updated description"

    # Act
    updated_item = ItemService.update_item(db_session, item.id, updated_name, updated_description, None)

    # Assert
    assert updated_item.name == updated_name
    assert updated_item.description == updated_description


def test_update_item_not_found(db_session: Session):
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        ItemService.update_item(db_session, 9999, "Updated Item", "Updated description", None)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Item not found"


def test_get_item_success(db_session: Session):
    # Arrange
    mock_file = MagicMock()
    mock_file.filename = "file.txt"
    with patch("shutil.copyfileobj", MagicMock()):
        item = ItemService.create_item(db_session, "Item to Get", "Description", mock_file)

    # Act
    retrieved_item = ItemService.get_item(db_session, item.id)

    # Assert
    assert retrieved_item.id == item.id
    assert retrieved_item.name == "Item to Get"
    assert retrieved_item.description == "Description"


def test_get_item_not_found(db_session: Session):
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        ItemService.get_item(db_session, 9999)  # Non-existent item ID

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Item not found"


def test_download_item_success(db_session: Session):
    # Arrange
    mock_file = MagicMock()
    mock_file.filename = "file.txt"

    # Mock file-related operations in create_item
    with patch("shutil.copyfileobj", MagicMock()), \
            patch("app.services.item_service.os.makedirs", MagicMock()):
        item = ItemService.create_item(db_session, "Item to Download", "Description", mock_file)

    # Simulate that the file exists
    with patch("app.services.item_service.os.path.exists", return_value=True):
        # Act
        file_path = ItemService.download_item(db_session, item.id)

    # Assert
    assert file_path == item.file_path


def test_download_item_file_not_found(db_session: Session):
    # Arrange
    mock_file = MagicMock()
    mock_file.filename = "file.txt"

    # Mock file-related operations in create_item
    with patch("shutil.copyfileobj", MagicMock()), \
            patch("app.services.item_service.os.makedirs", MagicMock()):
        item = ItemService.create_item(db_session, "Item to Download", "Description", mock_file)

    # Simulate that the file does not exist
    with patch("app.services.item_service.os.path.exists", return_value=False):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            ItemService.download_item(db_session, item.id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "File not found on server"


def test_delete_item_success(db_session: Session):
    # Arrange
    mock_file = MagicMock()
    mock_file.filename = "file.txt"
    with patch("shutil.copyfileobj", MagicMock()):
        item = ItemService.create_item(db_session, "Item to Delete", "Description", mock_file)

    # Act
    result = ItemService.delete_item(db_session, item.id)

    # Assert
    assert result["message"] == "Item deleted successfully"


def test_delete_item_not_found(db_session: Session):
    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        ItemService.delete_item(db_session, 9999)  # Non-existent item ID

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Item not found"
