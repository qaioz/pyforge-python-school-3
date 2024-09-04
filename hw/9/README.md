# Homework 10

## Celery

<img title="a title" alt="Alt text" src="../../images/9.png">


**Celery** is a distributed task queue framework that allows you to execute long-running tasks asynchronously, outside of the main application flow. It’s particularly useful for handling background jobs, such as sending emails, processing images, running machine learning models, or any computationally intensive work that you don’t want to block the main application.

**Key benefits of using Celery:**
- **Asynchronous execution:** Run tasks in the background without waiting for them to finish.
- **Distributed task execution:** Celery can distribute work across multiple workers on different machines.
- **Retry mechanisms:** Celery provides automatic retry on failure.
- **Integration with various brokers:** Celery supports multiple message brokers such as Redis, RabbitMQ, etc.

---

## Celery by example:

### Step 1: Setting Up the Environment

#### 1.1 Create Project Structure

1. Start by creating the following project structure:

```
/celery-fastapi-redis/
│
├── app/
│   ├── __init__.py
│   ├── main.py       # FastAPI app
│   ├── celery_worker.py   # Celery configuration
│   └── tasks.py      # Celery tasks
│
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

### Step 2: Celery Setup with FastAPI and Redis

#### 2.1 Define Dependencies

In `requirements.txt`, define the necessary dependencies:

```txt
fastapi
uvicorn
celery[redis]
redis
```

#### 2.2 Create FastAPI Application (`main.py`)

Create a simple **FastAPI** application that will handle API requests and interact with **Celery**.

```python
# app/main.py

from fastapi import FastAPI
from app.tasks import add_task
from celery.result import AsyncResult
from app.celery_worker import celery

app = FastAPI()

@app.post("/tasks/add")
async def create_task(x: int, y: int):
    task = add_task.delay(x, y)
    return {"task_id": task.id, "status": task.status}

@app.get("/tasks/{task_id}")
async def get_task_result(task_id: str):
    task_result = AsyncResult(task_id, app=celery)
    if task_result.state == 'PENDING':
        return {"task_id": task_id, "status": "Task is still processing"}
    elif task_result.state == 'SUCCESS':
        return {"task_id": task_id, "status": "Task completed", "result": task_result.result}
    else:
        return {"task_id": task_id, "status": task_result.state}
```

#### 2.3 Define Celery Worker (`celery_worker.py`)

Create a Celery configuration file to set up the Redis broker.

```python
# app/celery_worker.py

from celery import Celery

celery = Celery(
    'tasks',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)

celery.conf.update(task_track_started=True)
```

#### 2.4 Define Celery Task (`tasks.py`)

Now, define a simple Celery task, such as adding two numbers together.

```python
# app/tasks.py

from app.celery_worker import celery

@celery.task
def add_task(x: int, y: int):
    return x + y
```

---

### Step 3: Dockerizing the Application

We'll use **Docker** to containerize the FastAPI app, Celery worker, and Redis broker.

#### 3.1 Create `Dockerfile`

Define a `Dockerfile` to create a Docker image for the FastAPI app:

```Dockerfile
# Dockerfile

FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 3.2 Create `docker-compose.yml`

Use **Docker Compose** to define services for FastAPI, Celery, and Redis:

```yaml
# docker-compose.yml

version: '3.8'

services:
  fastapi:
    build: .
    ports:
      - "8000:8000"
    depends_on:
      - redis
    volumes:
      - .:/app

  celery_worker:
    build: .
    command: celery -A app.celery_worker worker --loglevel=info
    depends_on:
      - redis
    volumes:
      - .:/app

  redis:
    image: "redis:alpine"
    ports:
      - "6379:6379"
```

---

### Step 4: Running the Application

1. **Build and start the containers:**

   ```bash
   docker-compose up --build
   ```

   This will start the FastAPI app, Celery worker, and Redis container.

2. **Testing the application:**

   - Open your browser or use `curl` to send a POST request to add a task:

     ```bash
     curl -X POST "http://127.0.0.1:8000/tasks/add" -H "Content-Type: application/json" -d "{\"x\": 5, \"y\": 10}"
     ```

   - You will receive a response with the `task_id`. To check the status of the task, use:

     ```bash
     curl -X GET "http://127.0.0.1:8000/tasks/{task_id}"
     ```

   This will show whether the task is still processing, completed, or failed.

---


### Homework Assignment

**Objective**: Modify the substructure search functionality in your FastAPI project to use Celery.
It is necessary to modify the API. Our logic will be as follows: 
we will send a request to start the substructure search task and 
then we can send request to get results if it is ready as shown in the example.

All the following homework can be done in one request!

Don't forget to create a new branch and make a pull request.
Reviewers is [Dmitri Jakovlev](https://github.com/JDima)
