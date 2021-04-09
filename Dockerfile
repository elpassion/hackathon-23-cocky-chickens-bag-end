FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN apt-get update
RUN apt-get install -y wait-for-it

RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY poetry.lock .
COPY pyproject.toml .

RUN poetry install
COPY ./app /app

