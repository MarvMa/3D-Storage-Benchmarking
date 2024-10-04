from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Collection, Item, CollectionItem
from app.services.collections_service import CollectionService


def test_create_collection_success(db_session: Session):
    # Arrange
    name = "Test Collection"
    description = "Test description"

    # Act
    with patch.object(db_session, 'add', return_value=None):
        with patch.object(db_session, 'commit', return_value=None):
            with patch.object(db_session, 'refresh', return_value=None):  # Mock db.refresh
                collection = CollectionService.create_collection(db_session, name, description)

    # Assert
    assert collection.name == name
    assert collection.description == description


def test_create_collection_failure(db_session: Session):
    # Arrange
    name = None  # Invalid name
    description = "Test description"

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        CollectionService.create_collection(db_session, name, description)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Collection name is required"


def test_add_items_to_collection_success(db_session: Session):
    # Arrange
    collection_id = 1
    item_ids = [1, 2, 3]
    collection = Collection(id=collection_id, name="Test Collection")

    # Mock queries for collection and items
    with patch.object(db_session, 'query', side_effect=[
        MagicMock(filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=collection)))),
        MagicMock(filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=Item(id=1))))),
        MagicMock(filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=Item(id=2))))),
        MagicMock(filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=Item(id=3))))),
        MagicMock(filter_by=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))),
        MagicMock(filter_by=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))),
        MagicMock(filter_by=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))),
    ]):
        # Act
        with patch.object(db_session, 'add', return_value=None):
            with patch.object(db_session, 'commit', return_value=None):
                result = CollectionService.add_items_to_collection(db_session, collection_id, item_ids)

    # Assert
    assert result.id == collection_id
    assert result.name == "Test Collection"


def test_add_items_to_collection_collection_not_found(db_session: Session):
    # Arrange
    collection_id = 1
    item_ids = [1, 2, 3]

    with patch.object(db_session, 'query', side_effect=[
        MagicMock(filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))),
    ]):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            CollectionService.add_items_to_collection(db_session, collection_id, item_ids)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Collection not found"


def test_add_items_to_collection_item_not_found(db_session: Session):
    # Arrange
    collection_id = 1
    item_ids = [1, 2, 3]
    collection = Collection(id=collection_id, name="Test Collection")

    with patch.object(db_session, 'query', side_effect=[
        MagicMock(filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=collection)))),
        # Collection found
        MagicMock(filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=Item(id=1))))),
        MagicMock(filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))),
        MagicMock(filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))),
    ]):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            CollectionService.add_items_to_collection(db_session, collection_id, item_ids)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Item with id 2 not found"


def test_add_items_to_collection_duplicate_items(db_session: Session):
    # Arrange
    collection_id = 1
    item_ids = [1, 2]
    collection = Collection(id=collection_id, name="Test Collection")

    with patch.object(db_session, 'query', side_effect=[
        MagicMock(filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=collection)))),
        MagicMock(filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=Item(id=1))))),
        MagicMock(filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=Item(id=2))))),
        MagicMock(filter_by=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))),
        MagicMock(filter_by=MagicMock(return_value=MagicMock(
            first=MagicMock(return_value=CollectionItem(collection_id=collection_id, item_id=2))))),
    ]):
        # Act
        with patch.object(db_session, 'add', return_value=None):
            with patch.object(db_session, 'commit', return_value=None):
                result = CollectionService.add_items_to_collection(db_session, collection_id, item_ids)

    # Assert
    assert result.id == collection_id
    assert result.name == "Test Collection"


def test_remove_items_from_collection_success(db_session: Session):
    # Arrange
    collection_id = 1
    item_ids = [1, 2]
    collection = Collection(id=collection_id, name="Test Collection")

    with patch.object(db_session, 'query', side_effect=[
        MagicMock(filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=collection)))),
        MagicMock(filter_by=MagicMock(return_value=MagicMock(
            first=MagicMock(return_value=CollectionItem(collection_id=collection_id, item_id=1))))),
        MagicMock(filter_by=MagicMock(return_value=MagicMock(
            first=MagicMock(return_value=CollectionItem(collection_id=collection_id, item_id=2))))),
    ]):
        # Act
        with patch.object(db_session, 'delete', return_value=None):
            with patch.object(db_session, 'commit', return_value=None):
                result = CollectionService.remove_items_from_collection(db_session, collection_id, item_ids)

        # Assert
        assert result.id == collection_id
        assert result.name == "Test Collection"


def test_remove_items_from_collection_collection_not_found(db_session: Session):
    # Arrange
    collection_id = 1
    item_ids = [1, 2]

    with patch.object(db_session, 'query', side_effect=[
        MagicMock(filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))),
    ]):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            CollectionService.remove_items_from_collection(db_session, collection_id, item_ids)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Collection not found"


def test_remove_items_from_collection_item_not_found(db_session: Session):
    # Arrange
    collection_id = 1
    item_ids = [1, 2]
    collection = Collection(id=collection_id, name="Test Collection")

    with patch.object(db_session, 'query', side_effect=[
        MagicMock(filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=collection)))),
        # Collection found
        MagicMock(filter_by=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))),
        # CollectionItem 1 not found
        MagicMock(filter_by=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))),
        # CollectionItem 2 not found
    ]):
        # Act
        with patch.object(db_session, 'commit', return_value=None):
            result = CollectionService.remove_items_from_collection(db_session, collection_id, item_ids)

        # Assert
        assert result.id == collection_id
        assert result.name == "Test Collection"


def test_update_collection_success(db_session: Session):
    # Arrange
    collection = Collection(id=1, name="Old Name", description="Old description")

    with patch.object(db_session, 'query', return_value=MagicMock(
            filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=collection))))):
        updated_name = "Updated Name"
        updated_description = "Updated description"

        # Act
        with patch.object(db_session, 'commit', return_value=None):
            with patch.object(db_session, 'refresh', return_value=None):
                updated_collection = CollectionService.update_collection(db_session, collection.id, updated_name,
                                                                         updated_description)

        # Assert
        assert updated_collection.name == updated_name
        assert updated_collection.description == updated_description


def test_update_collection_not_found(db_session: Session):
    with patch.object(db_session, 'query', return_value=MagicMock(
            filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None))))):
        updated_name = "Updated Name"
        updated_description = "Updated description"

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            CollectionService.update_collection(db_session, 9999, updated_name, updated_description)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Collection not found"


def test_get_collection_success(db_session: Session):
    # Arrange
    collection = Collection(id=1, name="Test Collection", description="Test description")

    with patch.object(db_session, 'query', return_value=MagicMock(
            filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=collection))))):
        # Act
        retrieved_collection = CollectionService.get_collection(db_session, collection.id)

        # Assert
        assert retrieved_collection.id == collection.id
        assert retrieved_collection.name == collection.name
        assert retrieved_collection.description == collection.description


def test_get_collection_not_found(db_session: Session):
    with patch.object(db_session, 'query', return_value=MagicMock(
            filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None))))):
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            CollectionService.get_collection(db_session, 9999)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Collection not found"


def test_list_collections_success(db_session: Session):
    # Arrange
    collection1 = Collection(id=1, name="Collection 1", description="Description 1")
    collection2 = Collection(id=2, name="Collection 2", description="Description 2")

    with patch.object(db_session, 'query',
                      return_value=MagicMock(all=MagicMock(return_value=[collection1, collection2]))):
        # Act
        collections = CollectionService.list_collections(db_session)

        # Assert
        assert len(collections) == 2
        assert collections[0].id == collection1.id
        assert collections[1].id == collection2.id


def test_delete_collection_success(db_session: Session):
    # Arrange
    collection = Collection(id=1, name="Test Collection", description="Test description")

    with patch.object(db_session, 'query', return_value=MagicMock(
            filter=MagicMock(return_value=MagicMock(first=MagicMock(return_value=collection))))):
        # Act
        with patch.object(db_session, 'delete', return_value=None):  # Mock db.delete
            with patch.object(db_session, 'commit', return_value=None):
                with patch.object(db_session, 'refresh', return_value=None):  # Mock db.refresh
                    result = CollectionService.delete_collection(db_session, collection.id)

        # Assert
        assert result == {"message": "Collection deleted successfully"}
