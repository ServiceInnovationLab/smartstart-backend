# smartstart-backend

[SmartStart](https://smartstart.services.govt.nz/) provides step-by-step information and support to
help users access the right services for them and their baby.

This repository is the back end. It uses Django, Django REST Framework and RealMe. There is a
separate repository for `smartstart-frontend`, a React JavaScript user interface.

## Development environments

If you are a Catalyst developer, please see
[the instructions](https://gitlab.catalyst.net.nz/lef/ops#setup-an-environment) for environment
setup, and the section below regarding RealMe bundles.

### Run site in virtualenv

*The following instructions assume you are on a Ubuntu Linux system.*

Clone this repository to a directory and use the `requirements.txt` file to set up your Python 3.x
virtual environment.

Set up settings:

    cp settings/local.py.example settings/local.py
    vim settings/local.py

The default database is sqlite, for which you don't need any setup.

Note that the Django `SECRET_KEY` setting is used everywhere for password hashing, CSRF tokens and
session keys, among other things, so you should set it to be something unique.

To set up the site for the first time, create the database tables with the Django `migrate` command,
and load the test users from the fixture:

    python manage.py migrate --fake-initial
    python manage.py loaddata test_users

users:

- admin/admin
- test/test

Run this site for dev:

    python manage.py runserver 0.0.0.0:8000

Then you can visit site at:

    http://127.0.0.1:8000

## RealMe integration

This application relies on the RealMe service for authentication. If you are dealing with the live
site (you are probably a Catalyst developer!) see the section below. Otherwise, please use the
[django-realme](https://pypi.python.org/pypi/django-realme/) package.

### Set up for MTS (Catalyst developers only)

Decrypt gpg file for MTS bundle, refer to `bundles/README.md` for details.
Then make sure following settings are right:

    BUNDLE_NAME = 'MTS'
    BUNDLES_ROOT = '/path/to/bundles'
    SITE_URL = 'https://mts-test.dev.boac.lef'

Then go to this url:

    /realme/metadata/

Save page to local as a text file, then upload it to:

    https://mts.realme.govt.nz/logon-mts/metadataupdate

Note: after uploading, it just verifies the file, you need to click a second `Import` button to
finally apply it.
