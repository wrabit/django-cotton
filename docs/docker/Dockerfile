ARG PLATFORM=linux/amd64

# ---- Tailwind Build Stage (build is quicker like this vs installing npm, node separately) ----
FROM node:16-slim AS build_tailwind
WORKDIR /css
COPY package*.json ./
RUN npm install
COPY . .
RUN ["npx", "tailwindcss", "-o", "./docs_project/static/app.css"]

# Use an official Python runtime as a base image
FROM python:3.10-slim

# Keep logs unbuffered
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Install Poetry
RUN pip install --upgrade pip \
    && pip install poetry

# Copy only dependencies definition to the docker image
COPY . /app/

# Install project dependencies
RUN poetry config virtualenvs.create false \
    && poetry install

RUN SECRET_KEY=dummy STATIC_URL='/staticfiles/' python manage.py collectstatic --noinput --verbosity 2

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]