

FROM python:3.12
# add maintaner information and other important information

LABEL maintainer="gaiozi tabatadzegaga@gmail.com"
LABEL description="This image requires postgres database to start:\n\
 You can override DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, and DB_URL environment variables to connect to your database \n\
 If you start from docker compose, make sure correct database schema is created before starting the container, \n\
 One way to do this is if you use compose, you can override the entrypoint to run the migration script before starting the server  \n\
 If you do this alwas include fastapi run src/main.py in the entrypoint example  \n\
 entrypoint: ['/bin/sh', '-c', 'alembic upgrade head && fastapi run src/main.py']"

# Install rdkit library with pip, This is a big library and takes a while to install,
# so  I think it's better to install it before copying the rest of the dependencies,

RUN pip install rdkit

WORKDIR /app/

COPY requirements.txt .

RUN pip install -r requirements.txt

# Make sure alembic versions are generated before copying the src directory
COPY . .

EXPOSE 8000

ENTRYPOINT ["fastapi", "run", "src/main.py"]
#ENTRYPOINT ["ls"]

