#!/bin/bash
set -x

source /srv/env/bin/activate
cd /srv/backend
git pull
python manage.py migrate --fake-initial
python manage.py collectstatic --noinput
sudo touch /etc/uwsgi/vassals/backend.ini
sudo tail -n 50 -f /var/log/syslog
