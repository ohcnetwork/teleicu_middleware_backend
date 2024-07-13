FROM python:3.11-slim-bullseye

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

ENV PATH /venv/bin:$PATH

RUN python -m venv /venv
RUN pip install pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --categories "packages dev-packages"

COPY . /app

#add health check

WORKDIR /app

EXPOSE 8000

# runs the production server
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]