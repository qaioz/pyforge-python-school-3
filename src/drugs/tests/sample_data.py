from src.drugs.model import QuantityUnit
from src.drugs.schema import DrugMoleculeRequest, DrugRequest
from src.molecules.schema import MoleculeRequest

"""
Be sure to add theses molecules in the database one by one in the order they are defined here.

It must result in the consequent molecule_ids starting from 1.
"""

caffeine_request = MoleculeRequest.model_validate(
    {"name": "Caffeine", "smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"}
)

water_request = MoleculeRequest.model_validate({"name": "Water", "smiles": "O"})

sugar_request = MoleculeRequest.model_validate(
    {"name": "Sugar", "smiles": "C(C1C(C(C(C(O1)OC2(C(C(C(O2)CO)O)O)CO)O)O)O)O"}
)

ethanol_request = MoleculeRequest.model_validate({"name": "Ethanol", "smiles": "CCO"})

coffe_request = DrugRequest(
    name="Coffe",
    description="Best drug ever",
    molecules=[
        DrugMoleculeRequest(
            molecule_id=1, quantity=0.2, quantity_unit=QuantityUnit.MASS
        ),
        DrugMoleculeRequest(
            molecule_id=2, quantity=0.3, quantity_unit=QuantityUnit.VOLUME
        ),
        DrugMoleculeRequest(
            molecule_id=3, quantity=0.1, quantity_unit=QuantityUnit.MOLAR
        ),
    ],
)

drunkenstein = DrugRequest(
    name="Drunkenstein",
    description="contains 95% ethanol",
    molecules=[
        DrugMoleculeRequest(
            molecule_id=2, quantity=5, quantity_unit=QuantityUnit.VOLUME
        ),
        DrugMoleculeRequest(
            molecule_id=4, quantity=95, quantity_unit=QuantityUnit.VOLUME
        ),
    ],
)


sample1 = DrugRequest(
    name="Sample1",
    description="contains 90% ethanol",
    molecules=[
        DrugMoleculeRequest(
            molecule_id=2, quantity=10, quantity_unit=QuantityUnit.VOLUME
        ),
        DrugMoleculeRequest(
            molecule_id=4, quantity=90, quantity_unit=QuantityUnit.VOLUME
        ),
    ],
)


sample2 = DrugRequest(
    name="Sample2",
    description="contains 80% ethanol",
    molecules=[
        DrugMoleculeRequest(
            molecule_id=2, quantity=20, quantity_unit=QuantityUnit.VOLUME
        ),
        DrugMoleculeRequest(
            molecule_id=4, quantity=80, quantity_unit=QuantityUnit.VOLUME
        ),
    ],
)


sample3 = DrugRequest(
    name="Sample3",
    description="contains 70% ethanol",
    molecules=[
        DrugMoleculeRequest(
            molecule_id=2, quantity=30, quantity_unit=QuantityUnit.VOLUME
        ),
        DrugMoleculeRequest(
            molecule_id=4, quantity=70, quantity_unit=QuantityUnit.VOLUME
        ),
    ],
)
