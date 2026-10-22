# Sandbox image for Python live-coding exercises (runtime profile "python-pytest").
# The API copies the learner's files plus trusted tests into /workspace and runs this image.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Libraries the course teaches (FastAPI/Pydantic/SQLAlchemy/httpx/NumPy) so exercises can use them offline.
RUN pip install \
        "pytest==8.4.*" \
        "pytest-asyncio==1.*" \
        "anyio==4.*" \
        "httpx==0.28.*" \
        "respx==0.22.*" \
        "fastapi==0.115.*" \
        "pydantic==2.*" \
        "pydantic-settings==2.*" \
        "sqlalchemy==2.0.*" \
        "aiosqlite==0.21.*" \
        "numpy==2.*" \
        "tenacity==9.*" \
        "freezegun==1.*"

WORKDIR /workspace

COPY run.sh /usr/local/bin/neuralascent-python-run
RUN chmod 0755 /usr/local/bin/neuralascent-python-run

ENTRYPOINT ["/usr/local/bin/neuralascent-python-run"]
