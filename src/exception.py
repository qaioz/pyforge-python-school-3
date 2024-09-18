class BadRequestException(Exception):
    """
    I did not introduce my own status codes, so 400 is thrown for all bad requests.
    This is like a generic class and makes handling exceptions easier.

    This class is inherited by exceptions like InvalidSmilesException and DuplicateSmilesException
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class UnknownIdentifierException(Exception):
    def __init__(self, identifier):
        self.identifier = identifier
        self.message = f"Unknown identifier {self.identifier}"
        super().__init__(self.message)
