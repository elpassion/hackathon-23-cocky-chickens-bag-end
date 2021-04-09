FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY poetry.lock .
COPY pyproject.toml .

RUN poetry install
COPY ./app /app

