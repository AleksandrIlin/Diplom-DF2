FROM python:3.12 AS builder

RUN apt-get update || echo "apt-get update failed" && \
    apt-get install -y curl dnsutils || echo "apt-get install failed" && \
    apt-get clean || echo "apt-get clean failed"


RUN curl -sSL https://install.python-poetry.org | python3 -


WORKDIR /app
ENV PATH="/root/.local/bin:${PATH}"
ENV PYTHONPATH="/app"
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_HTTP_TIMEOUT=60


COPY pyproject.toml poetry.lock* ./


RUN poetry install --no-root

COPY . .
