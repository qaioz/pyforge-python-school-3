from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from src.drugs import mapper
from src.drugs.repository import DrugRepository, get_drug_repository
from src.drugs.schema import DrugRequest, DrugResponse
from src.exception import BadRequestException, UnknownIdentifierException
from src.database import get_session_factory


class DrugService:

    def __init__(self, drug_repository: DrugRepository, session_factory):
        self._drug_repository = drug_repository
        self._session_factory = session_factory

    def save(self, drug: DrugRequest) -> DrugResponse:
        with self._session_factory() as session:
            try:
                drug = self._drug_repository.save(drug.model_dump(), session)
                ans = mapper.drug_to_response(drug)
                session.commit()
            except IntegrityError as e:
                """
                Here most probably if this exception is raised,
                it means that the molecule_id is not found in the database.
                But in case of any other exception, I will still provide other exception details to the user.
                """
                raise BadRequestException(
                    "Check if the molecules exist in the database. \n" + str(e)
                )
            return ans

    def find_by_id(self, drug_id: int) -> DrugResponse:
        """
        :param drug_id:
        :return drug:
        :raise UnknownIdentifierException: if the drug with the given id does not exist
        """
        with self._session_factory() as session:
            drug = self._drug_repository.find_by_id(drug_id, session)
            if drug is None:
                raise UnknownIdentifierException(drug_id)
            return mapper.drug_to_response(drug)

    def delete(self, drug_id: int) -> bool:
        """
        :param drug_id:
        :return:
        :raises UnknownIdentifierException: if the drug with the given id does not exist
        """
        with self._session_factory() as session:
            # this line checks if the drug exists and raises an exception if it does not
            drug = self._drug_repository.find_by_id(obj_id=drug_id, session=session)
            if not drug:
                raise UnknownIdentifierException(drug_id)
            ans = self._drug_repository.delete(session=session, obj_id=drug_id)
            session.commit()
            return ans

    def find_all(self, page: int = 0, page_size: int = 1000):
        with self._session_factory() as session:
            drugs = self._drug_repository.find_all(session, page, page_size)
            return [mapper.drug_to_response(drug) for drug in drugs]


def get_drug_service(
    drug_repository: Annotated[DrugRepository, Depends(get_drug_repository)],
    session_factory: Annotated[
        Depends(get_session_factory), Depends(get_session_factory)
    ],
):
    return DrugService(drug_repository, session_factory=session_factory)
