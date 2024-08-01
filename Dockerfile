# base image +1 layer
FROM continuumio/miniconda3

LABEL maintainer="GT <suiiii@gmail.com>"
LABEL description="Docker image for fastapi in memory molecules crud"

# copy the environment file to the docker image + 1 layer
# this file is generate by conda env export
COPY environment.yml .

# create the environment and  name it environment + 1 layer
RUN conda env create -f environment.yml  -n environment

# working directory + 1 layer
WORKDIR /app

# copy the source code to the docker image + 1 layer
COPY /src /app/src

# expose the port 8000
EXPOSE 8000

# conda run is the main executable, maybe I should have heft only conda in entrypoint? idk
# --no-capture-output is for showing fasapi app logs in the termial when container runs
ENTRYPOINT [ "conda", "run" ]
CMD ["--no-capture-output", "-n", "environment", "fastapi", "run", "src/main.py"]

