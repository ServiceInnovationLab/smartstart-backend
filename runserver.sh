#!/bin/bash
pip freeze -r requirements-dev.txt > requirements.txt
python manage.py makemigrations
python manage.py migrate --fake-initial
python manage.py loaddata phasemetadata test_users
python manage.py runserver 0.0.0.0:8000
