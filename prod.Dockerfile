FROM python:3.13-slim-bookworm AS base

ARG APP_HOME=/app
ARG BUILD_ENVIRONMENT="production"
ARG APP_VERSION="unknown"

ENV APP_HOME=${APP_HOME} \
    BUILD_ENVIRONMENT=${BUILD_ENVIRONMENT} \
    APP_VERSION=${APP_VERSION} \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIPENV_VENV_IN_PROJECT=1 \
    PIPENV_CACHE_DIR=/root/.cache/pip \
    PATH=${APP_HOME}/.venv/bin:$PATH

WORKDIR ${APP_HOME}

FROM base AS builder

RUN python -m venv ${APP_HOME}/.venv

COPY Pipfile Pipfile.lock ${APP_HOME}/

RUN --mount=type=cache,target=/root/.cache/pip pip install pipenv==2024.4.0
RUN --mount=type=cache,target=/root/.cache/pip pipenv install --deploy --categories "packages"

FROM base AS runtime

RUN addgroup --system django && \
    adduser --system --ingroup django django && \
    chown django:django ${APP_HOME}

COPY --from=builder --chown=django:django ${APP_HOME}/.venv ${APP_HOME}/.venv
COPY --chmod=0755 --chown=django:django ./scripts/*.sh ${APP_HOME}/
COPY --chown=django:django . ${APP_HOME}

USER django

EXPOSE 8090

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8090/ || exit 1

ENTRYPOINT ["python"]
CMD ["manage.py", "runserver", "0.0.0.0:8090"]
