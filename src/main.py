from fastapi import FastAPI
from src.middleware import register_middlewares
from src.molecules.router import router as molecule_router
from src.drugs.router import router as drug_router
from src.handler import register_exception_handlers
from src.config import setup_logging
from src.celery_worker import celery
setup_logging()

app = FastAPI()

# register the routers
app.include_router(molecule_router, prefix="/molecules")
app.include_router(drug_router, prefix="/drugs")

register_exception_handlers(app)
register_middlewares(app)


@app.get("/")
def get_server_id():
    from os import getenv

    return "Hello from  server " + getenv("SERVER_ID", "")


@app.get("/tasks/{task_id}")
def read_item(task_id: str):
    task = celery.AsyncResult(task_id)
    if task.state == "SUCCESS":
        return {"status": task.state, "result": task.result}
    else:
        return {"status": task.state}


# @app.on_event("startup")
# def add_3_molecules():
#     service = get_molecule_service(ge
#
#     if not (get_settings().DEV_MODE or get_settings().TEST_MODE):
#         return
#
#     # add caffeine, surcose and water molecules
#     try:
#         service.save(
#             MoleculeRequest.model_validate(
#                 {"smiles": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C", "name": "Caffeine"}
#             )
#         )
#     except DuplicateSmilesException:
#         pass
#
#     try:
#         service.save(
#             MoleculeRequest.model_validate(
#                 {"smiles": "C(C1C(C(C(C(O1)O)O)O)O)O", "name": "Sucrose"}
#             )
#         )
#     except DuplicateSmilesException:
#         pass
#
#     try:
#         service.save(MoleculeRequest.model_validate({"smiles": "O", "name": "Water"}))
#     except DuplicateSmilesException:
#         pass
