ARG PYTHON_VERSION=3.12
# Use an official Python runtime as a base image
FROM python:${PYTHON_VERSION}-slim-bookworm

ARG DJANGO_VERSION=4.2
# Setup env
ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_NO_CACHE_DIR=off \
    POETRY_NO_INTERACTION=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Set the working directory in the container
WORKDIR /app

# Install Poetry
RUN pip install "poetry==1.8.3"

# Copy only dependencies definition to the docker image
COPY . /app/

# Install project dependencies
RUN poetry config virtualenvs.create false \
    && poetry install \
    && pip install -U --pre "django==$DJANGO_VERSION.*"

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
