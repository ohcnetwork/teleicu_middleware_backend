# Stage 1: Build stage
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PATH /venv/bin:$PATH

# Create virtual environment
RUN python -m venv /venv

# Install pipenv and dependencies
RUN pip install --no-cache-dir pipenv

# Copy Pipfile and Pipfile.lock for dependency installation
COPY Pipfile Pipfile.lock ./

# Install only production dependencies
RUN pipenv install --system --deploy --ignore-pipfile

# Stage 2: Production stage
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PATH /venv/bin:$PATH

# Copy virtual environment from the builder stage
COPY --from=builder /venv /venv

# Copy the application code
COPY . /app

# Set the working directory
WORKDIR /app

# Expose the application port
EXPOSE 8090


CMD ["python", "manage.py" , "runserver" , "0.0.0.0:8090"]
