from typing import Type
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database import Base


class SQLAlchemyRepository:
    """
    Base class for all repositories that use SQLAlchemy.

    Session does not commit automatically, so the service should commit the session after the transaction is done.

    """

    def __init__(self, model_type: Type[Base]):
        self._model_type = model_type

    def find_by_id(self, obj_id, session):
        return session.get(self._model_type, obj_id)

    def find_all(self, session: Session, page=0, page_size=1000):
        """
        Find all instances of the model with pagination support

        :param page: Zero indexed page number
        :param page_size: Items per page
        :return: List of instances
        """

        stmt = select(self._model_type).limit(page_size).offset(page * page_size)
        result = session.execute(stmt).scalars().all()
        return result

    def filter(self, session, **kwargs):
        stmt = select(self._model_type).filter_by(**kwargs)
        ans = session.execute(stmt).scalars().all()
        return ans

    def save(self, session, data: dict):
        instance = self._model_type(**data)
        session.add(instance)
        return instance

    def update(self, session, obj_id, data: dict):
        instance = session.get(self._model_type, obj_id)
        for key, value in data.items():
            setattr(instance, key, value)
        session.refresh(instance)
        return instance

    def delete(self, session: Session, obj_id) -> bool:
        # TODO testing was successful, but double check how session.delete works,
        #  I assume now that if it fails, it will throw an exception
        """
        Delete an instance

        Currently system is designed so that service before deleting an instance,
        checks if the instance exists or not and then throws some service level exception, like
        UnknownIdentifierException.

        TODO I think in the future, I should remove this check and let the repository throw the exception,
        so the additional check in the service is not needed.

        :param session:
        :param obj_id: id of the instance to be deleted
        :return:  True if the instance is deleted, False otherwise
        """

        try:
            instance = session.get(self._model_type, obj_id)
            session.delete(instance)
            return True
        except Exception:
            return False
