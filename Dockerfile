FROM python:3.11 as builder

ENV \
  # python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  # pip:
  PIP_NO_CACHE_DIR=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PIP_DEFAULT_TIMEOUT=100 \
  # poetry:
  POETRY_VERSION=1.3.2 \
  POETRY_NO_INTERACTION=1 \
  POETRY_VIRTUALENVS_CREATE=false \
  POETRY_CACHE_DIR='/var/cache/pypoetry' \
  POETRY_HOME='/usr/local'

RUN apt-get update && apt-get upgrade -y \
    && curl -sSL 'https://install.python-poetry.org' | python - \
    && poetry --version \
  # Cleaning cache:
   && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
   && apt-get clean -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock /app/

RUN --mount=type=cache,target="$POETRY_CACHE_DIR" poetry version \
  # Install deps:
  && poetry run pip install -U pip \
  && poetry install --no-interaction --no-ansi --no-root

COPY . /app

CMD poetry run python3 main.py
