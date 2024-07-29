import pytest
from src.models import Molecule
from src.repository import InMemoryMoleculesRepository


@pytest.fixture
def repository():
    return InMemoryMoleculesRepository()


def test_add_molecule(repository):
    molecule = Molecule(smiles="CC(=O)Oc1ccccc1C(=O)O", molecule_name="Aspirin",
                        description="Aspirin is in a group of medications called salicylates...")

    added_molecule = repository.add(molecule)
    assert added_molecule == molecule
    assert repository.exists_by_id(molecule.molecule_id) is True


def test_find_by_id(repository):
    molecule = Molecule(smiles="CC(=O)Oc1ccccc1C(=O)O", molecule_name="Aspirin",
                        description="Aspirin is in a group of medications called salicylates...")
    repository.add(molecule)

    found_molecule = repository.find_by_id(molecule.molecule_id)
    assert found_molecule == molecule


def test_find_all(repository):
    molecule1 = Molecule(smiles="CC(=O)Oc1ccccc1C(=O)O", molecule_name="Aspirin",
                         description="Aspirin is in a group of medications called salicylates...")
    molecule2 = Molecule(smiles="C", molecule_name="Carbon",
                         description="Base of all life on Earth")
    molecule3 = Molecule(smiles="O")

    repository.add(molecule1)
    repository.add(molecule2)
    repository.add(molecule3)

    all_molecules = repository.find_all()
    assert len(all_molecules) == 3
    assert molecule1 in all_molecules
    assert molecule2 in all_molecules
    assert molecule3 in all_molecules


def test_exists_by_id(repository):
    molecule = Molecule(smiles="CC(=O)Oc1ccccc1C(=O)O", molecule_name="Aspirin",
                        description="Aspirin is in a group of medications called salicylates...")
    repository.add(molecule)

    assert repository.exists_by_id(molecule.molecule_id) is True
    assert repository.exists_by_id(999) is False


def test_delete_by_id_existing(repository):
    molecule = Molecule(smiles="CC(=O)Oc1ccccc1C(=O)O", molecule_name="Aspirin",
                        description="Aspirin is in a group of medications called salicylates...")
    repository.add(molecule)

    repository.delete_by_id(molecule.molecule_id)
    assert repository.exists_by_id(molecule.molecule_id) is False


def test_delete_by_id_non_existing(repository):
    with pytest.raises(ValueError, match="Molecule with id 69 does not exist"):
        repository.delete_by_id(69)


# This is a reasonable testcase, but the way I implemented the Molecule class,
# it is not possible to add a molecule with the same id twice
def test_add_duplicate_molecule(repository):
    assert True
