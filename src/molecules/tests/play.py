from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import get_settings
from src.molecules.repository import MoleculeRepository
import random
import logging

logger = logging.getLogger(__name__)

engine = create_engine(
    get_settings().DEV_DB_URL,
)
session_factory = sessionmaker(bind=engine, autocommit=False, autoflush=False)
molecule_repository = MoleculeRepository()


def populate_repo_with_random_alkane_data(n_of_alkanes=100):
    """
    Populates the database with random alkane data,
    Smiles are random length of C's with max length 300,
    and mass is 12 * length of C's

    Inserts in chunks of 10000
    """
    chunk_size = 100000
    max_length = 300

    molecules = []

    inserted = 0

    for _ in range(n_of_alkanes):
        smiles_length = random.randint(1, max_length)
        smiles = "C" * smiles_length
        mass = 12 * smiles_length
        molecules.append(
            {"name": f"Alkane {smiles_length}", "smiles": smiles, "mass": mass}
        )

        if len(molecules) == chunk_size:
            with session_factory() as session:
                molecule_repository.bulk_insert(session, molecules)
                session.commit()
                molecules.clear()
                inserted += chunk_size
                logger.info(f"Inserted {inserted}/{n_of_alkanes} alkanes")
                print(f"Inserted {inserted}/{n_of_alkanes} alkanes")
    if molecules:
        with session_factory() as session:
            molecule_repository.bulk_insert(session, molecules)
            molecules.clear()
            session.commit()
            logger.info(f"Inserted {inserted}/{n_of_alkanes} alkanes")
            print(f"Inserted {inserted}/{n_of_alkanes} alkanes")


populate_repo_with_random_alkane_data(3 * 10**6)

# Compare this snippet from src/molecules/tests/test_repository.py:
