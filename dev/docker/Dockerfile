ARG PLATFORM=linux/amd64

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

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]