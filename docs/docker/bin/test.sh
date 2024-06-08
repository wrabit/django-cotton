#!/usr/bin/env bash

docker exec -t cotton-docs-web python manage.py test $*
