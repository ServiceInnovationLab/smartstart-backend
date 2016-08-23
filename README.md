# BOAC: Birth Of A Child

Welcome to LEF/BOAC!

## Run site in virtualenv

*Following instructions assume you are on a Ubuntu Linux system*

Clone this repo to dir you like, I will use home dir in this doc:

    cd ~
    git clone git@gitlab.catalyst.net.nz:lef/backend.git
    cd backend

Now your code should be in ~/backend, and you are in it.

Bootstrap the system for system-wide dependencies:

    sudo env/bootstrap.sh

Create a python3 virtualenv in a dir you like, I will use ~/env in this doc:

    mkdir ~/env
    virtualenv -p /usr/bin/python3 ~/env/py3

Activate virtualenv:

    # for default bash shell:
    . ~/env/py3/bin/activate
    # or if you use fish shell:
    . ~/env/py3/bin/activate.fish

Install python packages:

    cd ~/backend
    pip install -U -r env/requirements.txt

Set up settings:

    cp local.py.example local.py
    vim local.py

The default db is sqlite, for which you don't need any setup.

But if you want to use PostgreSQL, you may need to install it and override the db settings in local.py.

Create or update database tables:

    python manage.py migrate --fake-initial

Load pre-made test users from fixture:

    python manage.py loaddata test_users.json

credentials:
- admin/admin
- test/test

Run this site for dev:

    python manage.py runserver 0.0.0.0:8000

Then you can visit site at:

    http://127.0.0.1:8000

## Set up for MTS
Decrypt gpg file for MTS bundle, refer to bundles/README.md for details.
Then make sure following settings are right:

    BUNDLE_NAME = 'MTS'
    BUNDLES_ROOT = '/path/to/bundles'
    SITE_URL = 'https://mts-test.dev.boac.lef'

Then go to this url:

    /sp/metadata/

Save page to local as a text file, then upload it to:

    https://mts.realme.govt.nz/logon-mts/metadataupdate

Note: after uploading, it just verify the file, you need to click a second import button to finally apply it.

## Run site in docker

Install docker:

    https://docs.docker.com/engine/installation/linux/ubuntulinux/

Install docker-compose:

    sudo pip install -U docker-compose

Build docker image:

    docker-compose build

Load pre-made test users from fixture:

    docker-compose run dj python manage.py loaddata test_users

Run the site:

    docker-compose up

Then you can visit site at:

    http://127.0.0.1:8000
