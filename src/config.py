import os
from dotenv import load_dotenv
import logging

path_to_dotenv = os.path.join(".env")
load_dotenv(dotenv_path=path_to_dotenv)

logging.basicConfig(level=logging.DEBUG, filename='app.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')


class Config:
    def __init__(self):
        self.HTTP_DATABASE_URL = None
        if not os.environ.get("HTTP_DATABASE_URL"):
            self.HTTP_DATABASE_URL = "http://localhost:69"
        else:
            self.HTTP_DATABASE_URL = os.environ.get("HTTP_DATABASE_URL")
        logging.debug(f"HTTP_DATABASE_URL: {self.HTTP_DATABASE_URL}")