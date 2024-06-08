#!/usr/bin/env bash

docker exec -t cotton-dev-app python manage.py test $*
