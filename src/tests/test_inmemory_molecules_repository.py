import pytest
import src.tests.sample_data as sample_data
from src.exceptions import RepositoryItemNotFountException
from src.repository.molecule_repositories import InMemoryMoleculesRepository


"""
Here are my Unit tests for the InMemoryMoleculesRepository class.
"""


@pytest.fixture
def repository():
    return InMemoryMoleculesRepository()


def test_initialization(repository):
    assert repository.size() == 0


def test_add(repository):
    mol = sample_data.molecule_model_aspirin()
    repository.add(mol)
    found = repository.find_by_id(mol.get_id())
    assert found == mol


def test_find_by_id_not_exists(repository):
    with pytest.raises(RepositoryItemNotFountException):
        repository.find_by_id(123)


def test_find_all(repository):
    mol1 = sample_data.molecule_model_aspirin()
    mol2 = sample_data.molecule_model_methane_no_name_no_description()
    mol3 = sample_data.molecule_model_methane_no_description_custom_id()
    repository.add(mol1)
    repository.add(mol2)
    repository.add(mol3)
    assert repository.find_all() == [mol1, mol2, mol3]


@pytest.mark.parametrize(
    "molecule",
    [
        sample_data.molecule_model_aspirin(),
        sample_data.molecule_model_methane_no_name_no_description(),
    ],
)
def test_exists_by_id_true(repository, molecule):
    repository.add(molecule)
    assert repository.exists_by_id(molecule.get_id())


def test_exists_by_id_false(repository):
    assert not repository.exists_by_id(123)


def test_delete_by_id(repository):
    mol = sample_data.molecule_model_aspirin()
    mol1 = sample_data.molecule_model_methane_no_name_no_description()
    repository.add(mol)
    repository.add(mol1)
    repository.delete_by_id(mol.get_id())
    assert repository.find_all() == [mol1]


def test_delete_by_id_not_exists(repository):
    with pytest.raises(RepositoryItemNotFountException):
        repository.delete_by_id(123)


def test_size(repository):
    mol = sample_data.molecule_model_aspirin()
    mol1 = sample_data.molecule_model_methane_no_name_no_description()
    repository.add(mol)
    repository.add(mol1)
    assert repository.size() == 2


def test_clear(repository):
    mol = sample_data.molecule_model_aspirin()
    mol1 = sample_data.molecule_model_methane_no_name_no_description()
    repository.add(mol)
    repository.add(mol1)
    repository.clear()
    assert repository.find_all() == []
