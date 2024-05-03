FROM python:3.11-slim

ENV PATH=/root/.poetry/bin:${PATH} \
    PYTHONPATH="${PYTHONPATH}:/app" \
    PIP_NO_CACHE_DIR=off \
    POETRY_VERSION=1.7.0 \
    POETRY_VIRTUALENVS_CREATE=false

RUN \
  apt-get update && \
  apt-get install -yqq wget gnupg2 gcc && \
  apt-get update && \
  pip install -U pip && \
  pip install pipenv && \
  pip install "poetry==$POETRY_VERSION" && \
  pip3 install -U "poetry" && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY entrypoint.sh main.py poetry.lock pyproject.toml alembic.ini ./
RUN poetry install
COPY app ./app
COPY onramp ./onramp
COPY migrations ./migrations

CMD ["sh", "entrypoint.sh"]
