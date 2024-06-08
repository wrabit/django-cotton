#!/usr/bin/env bash

# Determine script directory
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Change directory to project directory
cd $SCRIPT_DIR

docker compose -f ../docker-compose.yaml up "$@"
