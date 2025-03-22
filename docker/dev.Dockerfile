FROM python:3.13-slim-bookworm

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIPENV_CACHE_DIR=/root/.cache/pip

ENV PATH /venv/bin:$PATH

RUN python -m venv /venv
RUN pip install pipenv

COPY Pipfile Pipfile.lock ./
RUN --mount=type=cache,target=/root/.cache/pip pipenv install --system --categories "packages dev-packages"

COPY . /app

WORKDIR /app

EXPOSE 8090
