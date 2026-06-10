ARG PLATFORM=linux/amd64

# ---- Cotton UI sources Stage: generate cotton-ui.sources.css (needs Django + the kit) ----
FROM python:3.12-slim-bookworm AS cotton_sources
ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_NO_INTERACTION=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive
WORKDIR /app
RUN pip install "poetry==1.8.3"
COPY . /app/
RUN poetry config virtualenvs.create false \
    && poetry install
RUN SECRET_KEY=dummy STATIC_URL='/staticfiles/' python manage.py cotton_ui_sources

# ---- Tailwind Build Stage (node; never touches the kit, only the generated sources) ----
FROM node:20-slim AS build_tailwind
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
COPY --from=cotton_sources /app/cotton-ui.sources.css ./cotton-ui.sources.css
RUN ["npx", "@tailwindcss/cli", "-i", "app.css", "-o", "./docs_project/static/app.css", "--minify"]

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

# Bring in the CSS built above. app.css is not committed; CI builds it from the kit.
COPY --from=build_tailwind /app/docs_project/static/app.css /app/docs_project/static/app.css

# The docs serve only their own built app.css and the kit's cotton-ui.js, so skip the rest
# of the kit's static (its source CSS and minified bundle, which manifest storage can't resolve).
RUN SECRET_KEY=dummy STATIC_URL='/staticfiles/' python manage.py collectstatic --noinput --verbosity 2 \
    --ignore 'cotton-ui.css' --ignore 'cotton-ui.tokens.css' \
    --ignore 'cotton-ui.min.js' --ignore 'cotton-ui.min.js.map'

# Now uninstall with poetry the container version of django-cotton, leaving the local version when we're developing
RUN poetry remove django-cotton

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]
