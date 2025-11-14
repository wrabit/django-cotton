ARG PLATFORM=linux/amd64

# ---- Tailwind Build Stage (build is qui¬cker like this vs installing npm, node separately) ----
FROM node:16-slim AS build_tailwind
WORKDIR /css
COPY package*.json ./
RUN npm install
COPY . .
RUN ["npx", "tailwindcss", "-o", "./docs_project/static/app.css"]

# Use an official Python runtime as a base image
FROM python:3.12-slim-bookworm AS base

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
    && poetry install

RUN SECRET_KEY=dummy STATIC_URL='/staticfiles/' python manage.py collectstatic --noinput --verbosity 2

# Now uninstall with poetry the container version of django-cotton, leaving the local version when we're developing
RUN poetry remove django-cotton

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]