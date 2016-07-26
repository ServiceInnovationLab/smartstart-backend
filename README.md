# BOAC: Birth Of A Child

Welcome to LEF/BOAC!

## Steps to run site

*Following instructions assume you are on a Ubuntu Linux system*

Clone this repo to home dir:

    git clone git@gitlab.catalyst.net.nz:lef/backend.git

Now your code should be in ~/backend.

Bootstrap the system for system-wide dependencies:

    ~/backend/bin/bootstrap.sh

Install postgres and make sure the database exsits:

    # TODO: same server or not?

Create virtualenv:

    mkdir ~/env
    virtualenv -p /usr/bin/python3 ~/env/py3

Activate virtualenv:

    # for default bash shell:
    . ~/env/py3/bin/activate
    # or if you use fish shell:
    . ~/env/py3/bin/activate.fish

Install python packages:

    cd ~/backend
    pip install -U -r requirements.txt

Set up settings:

    cp which.py.example which.py
    vim which.py
    cp local.py.example local.py
    vim local.py

Create or update database tables:

    python manage.py migrate --fake-initial

Create a superuser:

    python manage.py createsuperuser

Or you can load a pre-made one from fixture:

    python manage.py loaddata test_users.json

credential: admin/admin

Run this site for dev:

    # TODO: how are we going to deploy dev site?
    python manage.py runserver 0.0.0.0:8000

Then you can visit site at:

    # TODO: how are we going to deploy dev site?
    http://127.0.0.1:8000
