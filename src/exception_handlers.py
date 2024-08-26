from fastapi import Request
from fastapi.responses import JSONResponse

import src.exceptions as exceptions


async def invalid_smiles_exception_handler(
    request: Request, exc: exceptions.InvalidSmilesException
) -> JSONResponse:
    return JSONResponse(status_code=400, content={"message": exc.message})


async def unknown_identifier_exception_handler(
    request: Request, exc: exceptions.UnknownIdentifierException
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"message": exc.message})
