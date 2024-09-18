from fastapi.encoders import jsonable_encoder
from starlette import status
from starlette.responses import JSONResponse
from fastapi import Request
from src.exception import BadRequestException, UnknownIdentifierException


def bad_request_exception_handler(request: Request, exc: BadRequestException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=jsonable_encoder({"detail": exc.message}),
    )


def unknown_identifier_exception_handler(
    request: Request, exc: UnknownIdentifierException
):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=jsonable_encoder({"detail": exc.message}),
    )


# def credentials_exception_handler(request: Request, exc: CredentialsException):
#     return JSONResponse(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         content=jsonable_encoder({"detail": exc.message}),
#     )
#
#
# def duplicate_email_exception_handler(request: Request, exc: DuplicateEmailException):
#     return JSONResponse(
#         status_code=status.HTTP_400_BAD_REQUEST,
#         content=jsonable_encoder({"detail": exc.message}),
#     )
#
#
# def email_not_found_exception_handler(request: Request, exc: EmailNotFoundException):
#     return JSONResponse(
#         status_code=status.HTTP_404_NOT_FOUND,
#         content=jsonable_encoder({"detail": exc.message}),
#     )
#
#
# def not_enough_permission_exception_handler(
#     request: Request, exc: NotEnoughPermissionException
# ):
#     return JSONResponse(
#         status_code=status.HTTP_403_FORBIDDEN,
#         content=jsonable_encoder({"detail": exc.message}),
#     )


def register_exception_handlers(app):
    app.add_exception_handler(BadRequestException, bad_request_exception_handler)
    app.add_exception_handler(
        UnknownIdentifierException, unknown_identifier_exception_handler
    )
