import os
import json
import uuid

import HTTP_database.src.exception as exception


class CollectionService:
    """
    TODO: FIX Potential bug: It is possible to create a collection with the name "collections" which will overwrite the collections.json file.
    TODO: This implementation is not efficient. We don't use memory to store the collections at all.
    TODO: Currently every deletion removes the entry from the file and shifts the rest of the entries. This is bad. Fix it.
    TODO: Fixed fields like collection name, document id, are not validated.
    """

    def __init__(self, base_path: str):
        self.base_path = base_path
        self.collections_dir_path = os.path.join(self.base_path, "collections")
        self.collections_file_path = os.path.join(self.collections_dir_path, "collections.json")

        # Ensure the given base path exists
        if not os.path.exists(self.base_path):
            raise FileNotFoundError(f"The directory {self.base_path} does not exist.")

        # Create the collections directory if it doesn't exist
        if not os.path.exists(self.collections_dir_path):
            os.makedirs(self.collections_dir_path)

        # Create the collections.json file if it doesn't exist
        if not os.path.exists(self.collections_file_path):
            with open(self.collections_file_path, "w") as file:
                file.write("")

    def exists_by_name(self, collection_name: str):
        # at this point we are sure that the collections.json file exists
        with open(self.collections_file_path, "r") as file:
            for line in file:
                if line.strip():  # Ensure the line is not empty
                    collection = json.loads(line)
                    print(collection["name"])
                    if collection["name"] == collection_name:
                        return True
        return False

    def create_collection(self, collection_name: str) -> None:
        print(f"Creating collection with name: {collection_name}")
        if self.exists_by_name(collection_name):
            raise exception.CollectionAlreadyExistsException(collection_name)

        # This should also create the file with the same name as the collection
        with open(os.path.join(self.collections_dir_path, collection_name + ".json"), "w") as file:
            file.write("")

        with open(self.collections_file_path, "a") as file:
            file.write(json.dumps({"name": collection_name, "size": 0}) + "\n")

    def get_collection(self, collection_name: str):
        with open(self.collections_file_path, "r") as file:
            for line in file:
                if line.strip():
                    collection = json.loads(line)
                    if collection["name"] == collection_name:
                        return collection
        raise exception.NoSuchCollectionException(collection_name)

    def get_collections(self):
        collections = []
        with open(self.collections_file_path, "r") as file:
            for line in file:
                if line.strip():
                    collections.append(json.loads(line))
        return collections

    def delete_collection(self, collection_name: str):
        if not self.exists_by_name(collection_name):
            raise exception.NoSuchCollectionException(collection_name)

        collections = self.get_collections()
        with open(self.collections_file_path, "w") as file:
            for collection in collections:
                if collection["name"] != collection_name:
                    file.write(json.dumps(collection) + "\n")

        # Delete the file associated with the collection
        os.remove(os.path.join(self.collections_dir_path, collection_name + ".json"))
        return None

    def update_collection(self, collection_name: str, new_collection: dict):
        if not self.exists_by_name(collection_name):
            raise exception.NoSuchCollectionException(collection_name)

        collections = self.get_collections()
        with open(self.collections_file_path, "w") as file:
            for collection in collections:
                if collection["name"] == collection_name:
                    file.write(json.dumps(new_collection) + "\n")
                else:
                    file.write(json.dumps(collection) + "\n")

        #         change the name of the file associated with the collection
        os.rename(os.path.join(self.collections_dir_path, collection_name + ".json"),
                  os.path.join(self.collections_dir_path, new_collection["name"] + ".json"))
        return None

    def exists_document(self, collection_name: str, document_id: str):
        if not self.exists_by_name(collection_name):
            raise exception.NoSuchCollectionException(collection_name)

        with open(os.path.join(self.collections_dir_path, collection_name + ".json"), "r") as file:
            for line in file:
                if line.strip():
                    document = json.loads(line)
                    if document["_document_id"] == str(document_id):
                        return True
        return False

    def add_document(self, collection_name: str, document: dict) -> str:
        """returns the document_id of the added document"""
        if not self.exists_by_name(collection_name):
            raise exception.NoSuchCollectionException(collection_name)


        document = CollectionService.__set_object_id(document)

        with open(os.path.join(self.collections_dir_path, collection_name + ".json"), "a") as file:
            file.write(json.dumps(document) + "\n")

        #         update the size of the collection
        new_collection = self.get_collection(collection_name)
        new_collection["size"] += 1
        self.update_collection(collection_name, new_collection)
        return document["_document_id"]

    def get_document(self, collection_name: str, document_id: str):
        if not self.exists_by_name(collection_name):
            raise exception.NoSuchCollectionException(collection_name)

        with open(os.path.join(self.collections_dir_path, collection_name + ".json"), "r") as file:
            for line in file:
                if line.strip():
                    document = json.loads(line)
                    if document["_document_id"] == str(document_id):
                        return document
        raise exception.NoSuchDocumentException(collection_name, document_id)

    def get_documents(self, collection_name: str):
        if not self.exists_by_name(collection_name):
            raise exception.NoSuchCollectionException(collection_name)

        documents = []
        with open(os.path.join(self.collections_dir_path, collection_name + ".json"), "r") as file:
            for line in file:
                if line.strip():
                    documents.append(json.loads(line))
        return documents

    def delete_document(self, collection_name: str, document_id: str):
        if not self.exists_by_name(collection_name):
            raise exception.NoSuchCollectionException(collection_name)

        if not self.exists_document(collection_name, document_id):
            raise exception.NoSuchDocumentException(collection_name, document_id)

        documents = self.get_documents(collection_name)
        with open(os.path.join(self.collections_dir_path, collection_name + ".json"), "w") as file:
            for document in documents:
                if document["_document_id"] != str(document_id):
                    file.write(json.dumps(document) + "\n")

        #         update the size of the collection
        new_collection = self.get_collection(collection_name)
        new_collection["size"] -= 1
        self.update_collection(collection_name, new_collection)
        return None

    def update_document(self, collection_name: str, document_id: str, new_document: dict):
        """Every field except the _document_id of the document will be updated."""
        if not self.exists_by_name(collection_name):
            raise exception.NoSuchCollectionException(collection_name)

        if not self.exists_document(collection_name, document_id):
            raise exception.NoSuchDocumentException(collection_name, document_id)

        # Ensure the _document_id is not changed
        new_document["_document_id"] = str(document_id)

        documents = self.get_documents(collection_name)
        with open(os.path.join(self.collections_dir_path, collection_name + ".json"), "w") as file:
            for document in documents:
                if document["_document_id"] == str(document_id):
                    file.write(json.dumps(new_document) + "\n")
                else:
                    file.write(json.dumps(document) + "\n")
        return None

    @staticmethod
    def __set_object_id(document: dict):
        document["_document_id"] = str(uuid.uuid4())
        return document
