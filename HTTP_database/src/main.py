from fastapi import FastAPI, Depends
from fastapi.exceptions import HTTPException
from HTTP_database.src.exception import CollectionAlreadyExistsException, NoSuchCollectionException, \
    NoSuchDocumentException, \
    ValidationException
from HTTP_database.src.schemas import CreateCollection, CreateDocument
from HTTP_database.src.service import CollectionService
from HTTP_database.src.dependencies import get_service

app = FastAPI()


@app.exception_handler(CollectionAlreadyExistsException)
async def collection_already_exists_exception_handler(request, exc: CollectionAlreadyExistsException):
    raise HTTPException(status_code=400, detail=exc.message)


@app.exception_handler(NoSuchCollectionException)
async def no_such_collection_exception_handler(request, exc: NoSuchCollectionException):
    raise HTTPException(status_code=404, detail=exc.message)


@app.exception_handler(NoSuchDocumentException)
async def no_such_document_exception_handler(request, exc: NoSuchDocumentException):
    raise HTTPException(status_code=404, detail=exc.message)


@app.exception_handler(ValidationException)
async def validation_exception_handler(request, exc: ValidationException):
    raise HTTPException(status_code=400, detail=exc.message)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/collections", status_code=201)
def create_collection(collection: CreateCollection, service: CollectionService = Depends(get_service)) -> dict:
    service.create_collection(collection.name)
    return {"message": "Collection created successfully"}


@app.get("/collections", status_code=200)
def get_collections(service: CollectionService = Depends(get_service)) -> dict:
    return {"collections": service.get_collections()}


@app.get("/collections/{collection_name}", status_code=200)
def get_collection(collection_name: str, service: CollectionService = Depends(get_service)) -> dict:
    return service.get_collection(collection_name)


@app.delete("/collections/{collection_name}", status_code=200)
def delete_collection(collection_name: str, service: CollectionService = Depends(get_service)) -> dict:
    service.delete_collection(collection_name)
    return {"message": "Collection deleted successfully"}


@app.put("/collections/{collection_name}", status_code=200)
def update_collection(collection_name: str, new_collection: CreateCollection,
                      service: CollectionService = Depends(get_service)) -> dict:
    service.update_collection(collection_name, new_collection.dict())
    return {"message": "Collection updated successfully"}


@app.post("/collections/{collection_name}/documents", status_code=201)
def create_document(collection_name: str, document: CreateDocument,
                    service: CollectionService = Depends(get_service)) -> dict:
    document_id = service.add_document(collection_name, document.__dict__)
    return {"message": "Document created successfully", "document_id": document_id}


@app.get("/collections/{collection_name}/documents/{document_id}", status_code=200)
def get_document(collection_name: str, document_id: str, service: CollectionService = Depends(get_service)) -> dict:
    return service.get_document(collection_name, document_id)


@app.get("/collections/{collection_name}/documents", status_code=200)
def get_documents(collection_name: str, service: CollectionService = Depends(get_service)) -> dict:
    return {"documents": service.get_documents(collection_name)}


@app.delete("/collections/{collection_name}/documents/{document_id}", status_code=200)
def delete_document(collection_name: str, document_id: str, service: CollectionService = Depends(get_service)) -> dict:
    service.delete_document(collection_name, document_id)
    return {"message": "Document deleted successfully"}


@app.put("/collections/{collection_name}/documents/{document_id}", status_code=200)
def update_document(collection_name: str, document_id: str, new_document: CreateDocument,
                    service: CollectionService = Depends(get_service)) -> dict:
    service.update_document(collection_name, document_id, new_document.dict())
    return {"message": "Document updated successfully"}
