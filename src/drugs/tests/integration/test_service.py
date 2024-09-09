import pytest
from unittest.mock import Mock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import get_settings
from src.drugs.repository import DrugRepository
from src.drugs.service import DrugService
from src.database import Base
from src.exception import BadRequestException, UnknownIdentifierException
from src.molecules.repository import MoleculeRepository
from src.molecules.service import MoleculeService
import src.drugs.tests.sample_data as sample_data

engine = create_engine(get_settings().TEST_DB_URL)
session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
repository = DrugRepository()
service = DrugService(repository, session_factory)

mock_redis = Mock()
mock_redis.get.return_value = None
molecule_repository = MoleculeRepository()
molecule_service = MoleculeService(molecule_repository, session_factory)


@pytest.fixture
def init_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    # add caffeine molecule
    molecule_service.save(sample_data.caffeine_request)
    # add water and sugar molecules
    molecule_service.save(sample_data.water_request)
    molecule_service.save(sample_data.sugar_request)
    molecule_service.save(sample_data.ethanol_request)
    yield
    Base.metadata.drop_all(engine)


def test_save(init_db):
    response = service.save(sample_data.coffe_request)
    assert response.name == sample_data.coffe_request.name
    assert response.description == sample_data.coffe_request.description
    assert len(response.molecules) == 3


def test_save_with_nonexistent_molecule(init_db):
    coffee_request = sample_data.coffe_request.__deepcopy__()
    coffee_request.molecules[0].molecule_id = 10232
    with pytest.raises(BadRequestException):
        service.save(coffee_request)


def test_find_by_id(init_db):
    response = service.save(sample_data.coffe_request)
    response = service.find_by_id(response.drug_id)
    assert response.name == sample_data.coffe_request.name
    assert response.description == sample_data.coffe_request.description
    assert len(response.molecules) == 3


def test_find_by_id_with_nonexistent_id(init_db):
    with pytest.raises(UnknownIdentifierException):
        service.find_by_id(1)


def test_delete(init_db):
    response = service.save(sample_data.coffe_request)
    deleted = service.delete(response.drug_id)
    assert deleted is True
    with pytest.raises(UnknownIdentifierException):
        service.find_by_id(response.drug_id)


def test_delete_with_nonexistent_id(init_db):
    with pytest.raises(UnknownIdentifierException):
        service.delete(1)


def test_find_all(init_db):
    coffe = service.save(sample_data.coffe_request)
    drunkenstein = service.save(sample_data.drunkenstein)

    response = service.find_all()
    assert len(response) == 2
    assert response[0].name == coffe.name
    assert response[1].name == drunkenstein.name
    assert response[1].molecules[0].quantity == drunkenstein.molecules[0].quantity
