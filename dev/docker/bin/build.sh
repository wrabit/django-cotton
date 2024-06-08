#!/bin/bash

# if arg exists 'mac', then build for mac
if [ "$1" = "mac" ]; then
    PLATFORM="linux/arm64"
else
    PLATFORM="linux/amd64"
fi

# Determine script directory
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Change directory to project directory
cd $SCRIPT_DIR

docker build --no-cache --build-arg PLATFORM=$PLATFORM -f ../Dockerfile ../../example_project -t cotton-test-app