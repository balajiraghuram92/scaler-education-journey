FROM python:3.12-slim
WORKDIR /srv
COPY pyproject.toml ./
RUN pip install --no-cache-dir /srv
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
EXPOSE 8000
