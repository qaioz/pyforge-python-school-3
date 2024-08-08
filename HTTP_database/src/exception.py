class CollectionAlreadyExistsException(Exception):

    def __init__(self, name: str):
        self.message = f"Collection with name '{name}' already exists."
        super().__init__(self.message)


class NoSuchCollectionException(Exception):

    def __init__(self, name: str):
        self.message = f"Collection with name '{name}' does not exist."
        super().__init__(self.message)


class NoSuchDocumentException(Exception):

    def __init__(self, collection_name: str, document_id: str):
        self.message = f"Document with ID '{document_id}' does not exist in collection '{collection_name}'."
        super().__init__(self.message)


class ValidationException(Exception):

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)