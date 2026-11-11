FROM python:3.12-slim

WORKDIR /app

COPY api-python/requirements.txt api-python/requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY api-python/ /app/api-python/
COPY exercises /app/exercises

WORKDIR /app/api-python
EXPOSE 8081
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]
