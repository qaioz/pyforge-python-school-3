import json
import os
import uuid

import pytest
import HTTP_database.src.exception as exception
from .service import CollectionService
from pytest_mock import MockerFixture


@pytest.fixture
def temp_directory(tmp_path):
    return tmp_path


@pytest.fixture
def collection_service(temp_directory):
    return CollectionService(base_path=temp_directory)


def test_init_throws_error_on_non_existing_base_path():
    # Test for a non-existing directory
    with pytest.raises(FileNotFoundError):
        CollectionService(base_path="'meaning of life' directory")


def test_init_creates_file(temp_directory):
    # Test if the collections directory and collections.json file are created
    CollectionService(base_path=temp_directory)
    assert (temp_directory / "collections" / "collections.json").exists()


def test_init_collections_dir_already_exists_but_the_json_does_not_exists_dir_not_created_and_file_not_created(
        temp_directory,
        mocker: MockerFixture):
    """This test has to check that collection directory and json file are not overwritten if already exist"""
    # Create the collections directory
    collections_dir_path = temp_directory / "collections"
    collections_dir_path.mkdir()

    # Create the collections.json file
    collections_file_path = collections_dir_path / "collections.json"
    collections_file_path.touch()

    # Mock the os.makedirs function
    mkdir = mocker.patch("os.makedirs")
    file_open = mocker.patch("builtins.open")

    # Create an instance of CollectionService
    CollectionService(base_path=temp_directory)

    # __init__ should not call os.makedirs, which means the directory is not created
    mkdir.assert_not_called()
    # __init__ should not call open, which means the file is not created
    file_open.assert_not_called()


def test_exists_by_name(temp_directory, mocker: MockerFixture):
    # Since we don't have the correctness of the collection creation, we will mock the file content of collections.json
    file_content = json.dumps({"name": "collection1", "size": 0}) + "\n  " + json.dumps(
        {"name": "collection2", "size": 0}) + "    \n"
    mock_open = mocker.mock_open(read_data=file_content)
    mocker.patch("builtins.open", mock_open)
    service = CollectionService(temp_directory)
    assert service.exists_by_name("collection1")
    assert service.exists_by_name("collection2")


def test_exists_by_name_not_found(collection_service):
    # Test for a non-existing collection
    assert not collection_service.exists_by_name("collection4")


def test_create_collection(collection_service):
    # Test for creating a collection
    collection_service.create_collection("collection1")
    assert collection_service.exists_by_name("collection1")


def test_create_collection_already_exists(collection_service):
    # Test for creating a collection that already exists
    collection_service.create_collection("collection1")
    with pytest.raises(exception.CollectionAlreadyExistsException):
        collection_service.create_collection("collection1")


def test_create_collection_creates_file(temp_directory):
    # Test if the collection file is created when a collection is created
    service = CollectionService(base_path=temp_directory)
    service.create_collection("collection1")
    assert (temp_directory / "collections" / "collection1.json").exists()


def test_get_collection(collection_service):
    # Test for getting a collection
    collection_service.create_collection("collection1")
    collection_service.create_collection("collection2")
    assert collection_service.get_collection("collection2") == {"name": "collection2", "size": 0}


def test_get_collection_not_found(collection_service):
    # Test for getting a non-existing collection
    collection_service.create_collection("collection1")
    collection_service.create_collection(" my savings ")
    with pytest.raises(exception.NoSuchCollectionException):
        collection_service.get_collection("my savings")


def test_get_collections(collection_service):
    # Test for getting all collections
    collection_service.create_collection("collection1")
    collection_service.create_collection("collection2")
    assert collection_service.get_collections() == [{"name": "collection1", "size": 0},
                                                    {"name": "collection2", "size": 0}]


def test_delete_collection(collection_service):
    # Test for deleting a collection
    collection_service.create_collection("collection1")
    collection_service.create_collection("collection2")
    collection_service.delete_collection("collection1")
    assert collection_service.get_collections() == [{"name": "collection2", "size": 0}]


def test_delete_collection_not_found(collection_service):
    # Test for deleting a non-existing collection
    collection_service.create_collection("collection1")
    with pytest.raises(exception.NoSuchCollectionException):
        collection_service.delete_collection("collection2")


def test_update_collection(collection_service):
    # Test for updating a collection
    collection_service.create_collection("collection1")
    collection_service.create_collection("collection2")
    collection_service.update_collection("collection1", {"name": "collection3", "size": 1})
    assert collection_service.get_collections() == [{"name": "collection3", "size": 1},
                                                    {"name": "collection2", "size": 0}]
    base_path = os.path.join(collection_service.base_path)
    assert not os.path.exists(os.path.join(base_path, "collections", "collection1.json"))
    assert os.path.exists(os.path.join(base_path, "collections", "collection3.json"))


def test_update_collection_not_found(collection_service):
    # Test for updating a non-existing collection
    collection_service.create_collection("collection1")
    with pytest.raises(exception.NoSuchCollectionException):
        collection_service.update_collection("collection2", {"name": "collection3", "size": 1})


def test_exists_document(collection_service, mocker: MockerFixture):
    # Test for checking if a document exists in a collection
    collection_service.create_collection("collection1")
    # mock the file content of collection1.json
    docs = [{"_document_id": str(uuid.uuid4()), "data": {"name": "doc1"}},
            {"_document_id": str(uuid.uuid4()), "data": {"name": "doc2"}}]
    file_content = json.dumps(docs[0]) + "\n" + json.dumps(docs[1])
    mock_open = mocker.mock_open(read_data=file_content)
    mocker.patch("builtins.open", mock_open)
    # patch the exists_by_name method to return True
    mocker.patch.object(CollectionService, "exists_by_name", return_value=True)
    assert collection_service.exists_document("collection1", docs[0]["_document_id"])


def test_exists_document_not_found(collection_service, mocker: MockerFixture):
    # Test for checking if a document exists in a collection
    collection_service.create_collection("collection1")
    # mock the file content of collection1.json
    docs = [{"_document_id": str(uuid.uuid4()), "data": {"name": "doc1"}},
            {"_document_id": str(uuid.uuid4()), "data": {"name": "doc2"}}]
    file_content = json.dumps(docs[0]) + "\n" + json.dumps(docs[1])
    mock_open = mocker.mock_open(read_data=file_content)
    mocker.patch("builtins.open", mock_open)
    # patch the exists_by_name method to return True
    mocker.patch.object(CollectionService, "exists_by_name", return_value=True)
    assert not collection_service.exists_document("collection1", str(uuid.uuid4()))


def test_exists_document_collection_not_found(collection_service):
    # Test for checking if a document exists in a non-existing collection
    with pytest.raises(exception.NoSuchCollectionException):
        collection_service.exists_document("collection1", str(uuid.uuid4()))


def test_add_document(collection_service):
    # Test for adding a document to a collection
    collection_service.create_collection("collection1")
    collection_service.create_collection("collection2")
    document = {"data": {"name": "doc1"}}
    document2 = {"data": {"name": "doc2"}}
    document3 = {"data": {"name": "doc3"}}
    collection_service.add_document("collection1", document)
    collection_service.add_document("collection1", document2)
    collection_service.add_document("collection2", document3)
    assert collection_service.get_collection("collection1") == {"name": "collection1", "size": 2}
    assert collection_service.get_collection("collection2") == {"name": "collection2", "size": 1}
    assert collection_service.exists_document("collection1", document["_document_id"])
    assert collection_service.exists_document("collection1", document2["_document_id"])
    assert collection_service.exists_document("collection2", document3["_document_id"])


def test_add_document_collection_not_found(collection_service):
    # Test for adding a document to a non-existing collection
    with pytest.raises(exception.NoSuchCollectionException):
        collection_service.add_document("collection1", {"data": {"name": "doc1"}})


# parametrize the test for (doc,expected)
@pytest.mark.parametrize("doc,expected", [
    ({"data": {"name": "doc1"}}, {"data": {"name": "doc1"}}),
    ({"data": {"name": "doc2"}}, {"data": {"name": "doc2"}}),
    ({"data": {"name": "doc3"}}, {"data": {"name": "doc3"}}),
])
def test_get_document(collection_service, doc, expected):
    # Test for getting a document from a collection
    collection_service.create_collection("collection1")
    document_id = collection_service.add_document("collection1", doc)
    assert collection_service.get_document("collection1", document_id)["data"] == expected["data"]


def test_get_document_not_found(collection_service):
    # Test for getting a non-existing document from a collection
    collection_service.create_collection("collection1")
    collection_service.add_document("collection1", {"data": {"name": "doc1"}})
    with pytest.raises(exception.NoSuchDocumentException):
        collection_service.get_document("collection1", str(uuid.uuid4()))


def test_get_documents(collection_service):
    # Test for getting all documents from a collection
    collection_service.create_collection("collection1")
    doc1 = {"data": {"name": "doc1"}}
    doc2 = {"data": {"name": "doc2"}}
    collection_service.add_document("collection1", doc1)
    collection_service.add_document("collection1", doc2)
    assert collection_service.get_documents("collection1") == [doc1, doc2]


def test_get_documents_not_found(collection_service):
    # Test for getting all documents from a non-existing collection
    with pytest.raises(exception.NoSuchCollectionException):
        collection_service.get_documents("collection1")


def test_delete_document(collection_service):
    # Test for deleting a document from a collection
    collection_service.create_collection("collection1")
    doc1 = {"data": {"name": "doc1"}}
    doc2 = {"data": {"name": "doc2"}}
    document_id1 = collection_service.add_document("collection1", doc1)
    document_id2 = collection_service.add_document("collection1", doc2)
    collection_service.delete_document("collection1", document_id1)
    assert collection_service.get_collection("collection1") == {"name": "collection1", "size": 1}
    assert not collection_service.exists_document("collection1", document_id1)
    assert collection_service.exists_document("collection1", document_id2)


def test_delete_document_not_found(collection_service):
    # Test for deleting a non-existing document from a collection
    collection_service.create_collection("collection1")
    collection_service.add_document("collection1", {"data": {"name": "doc1"}})
    with pytest.raises(exception.NoSuchDocumentException):
        collection_service.delete_document("collection1", str(uuid.uuid4()))


def test_delete_document_collection_not_found(collection_service):
    # Test for deleting a document from a non-existing collection
    with pytest.raises(exception.NoSuchCollectionException):
        collection_service.delete_document("collection1", str(uuid.uuid4()))


def test_update_document(collection_service):
    # Test for updating a document in a collection
    collection_service.create_collection("collection1")
    doc1 = {"data": {"name": "doc1"}}
    doc2 = {"data": {"name": "doc2"}}
    document_id1 = collection_service.add_document("collection1", doc1)
    collection_service.add_document("collection1", doc2)
    collection_service.update_document("collection1", document_id1, {"data": {"name": "doc3"}})
    assert collection_service.get_document("collection1", document_id1)["data"] == {"name": "doc3"}


def test_update_document_not_found(collection_service):
    # Test for updating a non-existing document in a collection
    collection_service.create_collection("collection1")
    collection_service.add_document("collection1", {"data": {"name": "doc1"}})
    with pytest.raises(exception.NoSuchDocumentException):
        collection_service.update_document("collection1", str(uuid.uuid4()), {"data": {"name": "doc3"}})


def test_update_document_collection_not_found(collection_service):
    # Test for updating a document in a non-existing collection
    with pytest.raises(exception.NoSuchCollectionException):
        collection_service.update_document("collection1", str(uuid.uuid4()), {"data": {"name": "doc3"}})

