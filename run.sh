#!/bin/bash

python manage.py migrate --fake-initial
python manage.py runserver 0.0.0.0:8000
