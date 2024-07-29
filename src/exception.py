
class UnknownIdentifierException(Exception):
    def __init__(self, identifier: int):
        self.identifier = identifier
        super().__init__(f"Unknown identifier: {identifier}")


class InvalidSmilesException(Exception):
    def __init__(self, smiles: str):
        self.smiles = smiles
        super().__init__(f"Invalid SMILES string: {smiles}")
