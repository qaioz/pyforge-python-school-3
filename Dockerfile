FROM continuumio/miniconda3

# copy the environment file to the docker image
COPY environment.yml .

# create the environment file and  name it environment
RUN conda env create -f environment.yml  -n environment

# copy the source code to the docker image
COPY . .

# expose the port 8000
EXPOSE 8000

# run fastapi
ENTRYPOINT [ "conda", "run" ]
CMD ["-n", "environment", "fastapi", "run", "src/main.py"]

