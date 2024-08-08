import os
from dotenv import load_dotenv

path_to_dotenv = os.path.join("HTTP_database", ".env")
load_dotenv(dotenv_path=path_to_dotenv)


# if BASE_DIRECTORY_CREATE_TYPE == "create" should recreate the directory, if it exists,
# if BASE_DIRECTORY_CREATE_TYPE == "update" should create the directory if it does not exist

class Config:
    def __init__(self):
        self.BASE_DIRECTORY = None
        if not os.environ.get("BASE_DIRECTORY"):
            self.BASE_DIRECTORY = os.path.join(os.getcwd(), "HTTP_database", "var", "data")
        else:
            self.BASE_DIRECTORY = os.environ.get("BASE_DIRECTORY")
        self.BASE_DIRECTORY_CREATE_TYPE = os.environ.get("BASE_DIRECTORY_CREATE_TYPE", "update")
        self.init()

    def init(self):
        if self.BASE_DIRECTORY_CREATE_TYPE == "create":
            if os.path.exists(self.BASE_DIRECTORY):
                os.rmdir(self.BASE_DIRECTORY)
            os.makedirs(self.BASE_DIRECTORY)

        if self.BASE_DIRECTORY_CREATE_TYPE == "update":
            if not os.path.exists(self.BASE_DIRECTORY):
                os.makedirs(self.BASE_DIRECTORY)

        if self.BASE_DIRECTORY_CREATE_TYPE not in ["create", "update"]:
            raise ValueError("Invalid value for BASE_DIRECTORY_CREATE_TYPE")
