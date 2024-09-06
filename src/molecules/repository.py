from functools import lru_cache

from sqlalchemy import text, insert
from sqlmodel import Session

from src.molecules.model import Molecule
from src.molecules.schema import SearchParams
from src.repository import SQLAlchemyRepository
import logging

logger = logging.getLogger(__name__)


class MoleculeRepository(SQLAlchemyRepository):
    def __init__(self):
        super().__init__(Molecule)

    def find_all(
        self,
        session: Session,
        page=0,
        page_size=1000,
        search_params: SearchParams = None,
    ):
        """
        If name is provided, then fuzzy search with trigrams is performed, results are ordered by similarity,
        notice that in that case, order_by and order are ignored. Filtering by mass is still possible.

        If name is not provided, then normal search is performed, results are ordered by order_by and order.

        Return type for now is a collection of ScalarResult, might include extra field "sml" for similarity,
        so be careful when using this method.

        //TODO: This append is not a good practice, but I will keep it for now, I saw there are nice patterns
        //TODO: in sql alchemy querying guide, I will try to implement them later.
        """

        min_mass_filter = (
            f" AND mass >= {search_params.min_mass}" if search_params.min_mass else ""
        )

        max_mass_filter = (
            f" AND mass <= {search_params.max_mass}" if search_params.max_mass else ""
        )

        name_filter = f" AND name % '{search_params.name}'"

        if search_params.name:
            query = f"""
                SELECT similarity('{search_params.name}',m.name) as sml, * FROM molecules m
                WHERE 1=1
                {min_mass_filter}
                {max_mass_filter}
                {name_filter}
                ORDER BY sml DESC
                LIMIT {page_size} OFFSET {page * page_size}
            """
        else:
            order_by = (
                f"ORDER BY {search_params.order_by}" if search_params.order_by else ""
            )
            order = (
                ""
                if not search_params.order_by
                else search_params.order if search_params.order else "ASC"
            )
            query = f"""
                SELECT * FROM molecules
                WHERE 1=1
                {min_mass_filter}
                {max_mass_filter}
                {order_by} {order}
                LIMIT {page_size} OFFSET {page * page_size}
            """

        return session.execute(text(query)).all()

    def bulk_insert(self, session: Session, data: list):
        """
        returns the int number of added rows, commits automatically

        //TODO: I was in rush for deadline, I will implement a better way to handle errors and let the user know what
        went wrong.
        """
        data = [{"mass": len(d["smiles"]), **d} for d in data]
        try:
            session.execute(insert(Molecule), data)
            session.flush()
        except Exception as e:
            session.rollback()
            logger.error(f"Error inserting data, no molecules will be added {e}")

        return len(data)


@lru_cache
def get_molecule_repository():
    return MoleculeRepository()
