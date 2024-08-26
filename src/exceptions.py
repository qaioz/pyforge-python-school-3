class UnknownIdentifierException(Exception):
    """This exception is raised at the API level when an unknown identifier is provided."""

    def __init__(self, identifier):
        self.identifier = identifier
        self.message = f"Unknown identifier: {identifier}"
        super().__init__(self.message)


class RepositoryItemNotFountException(Exception):
    """This exception is raised at the repository/service level when an item with the provided key is not found."""

    def __init__(self, key):
        self.key = key
        self.message = f"Repository item with the key: {key} not found"
        super().__init__(self.message)


class RepositoryItemAlreadyExistsException(Exception):
    """This exception is raised at the repository/service level when an item with the provided key is not found."""

    def __init__(self, key):
        self.key = key
        self.message = f"Repository item with the key: {key} already exists"
        super().__init__(self.message)


class InvalidSmilesException(Exception):
    def __init__(self, smiles):
        self.message = f"Invalid SMILES string: {smiles}"
        self.smiles = smiles
        super().__init__(self.message)


class HTTPClientException(Exception):
    def __init__(self, response_code, info=None):
        self.message = f"HTTP Client Exception: {response_code}"
        self.response_code = response_code
        super().__init__(self.message)
