FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN pip install poetry
COPY poetry.lock .
COPY pyproject.toml .

RUN poetry install
COPY ./app /app
