from src.exception import BadRequestException


class InvalidSmilesException(BadRequestException):
    def __init__(self, smiles):
        self.smiles = smiles
        self.message = (
            f"Smiles string {self.smiles} does not represent a valid molecule"
        )
        super().__init__(self.message)


class DuplicateSmilesException(BadRequestException):
    def __init__(self, smiles):
        self.smiles = smiles
        self.message = f"Smiles string {self.smiles} is not unique"
        super().__init__(self.message)


class InvalidCsvHeaderColumnsException(BadRequestException):
    def __init__(self, missing_columns):
        super().__init__(
            message=f"Following csv columns are missing from the header: {missing_columns}"
        )


class CsvLineParsingException(Exception):
    """
    THis will be thrown at the service level, when parsing invalid csv lines
    """

    def __init__(self, line):
        self.line = line
        self.message = f"CSV line {line} can not be parsed into the molecule"
