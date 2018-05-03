# monzo-duo

> Monzo app connecting two accounts (a bit like a joint account)

## Overview

Two Monzo bank customers can use this app to connect their accounts, giving (a lot of) insight into
each others' account usage, much like a joint account does.

## Technologies

Implemented in Python 2.7 on Google AppEngine and using Google DataStore, this is designed to fall
within the free tier that Google Cloud Platform provides.

### Project setup

1.  Create a [Google Cloud Platform](https://cloud.google.com/getting-started/) account, and set up a 'project' for this app; billing is not required. Set up the SDK on your local machine with the project details.
2.  Ensure you have `Python2.7` on your local machine (at least at the minor version that GAE runs), with `mkvirtualenv` and `pip`.
3.  Set up a virtualenv using this command from the project root: `mkvirtualenv -p python2.7 $(pwd)/venv`
4.  Activate the virtualenv (do this each coding session) with `source ./venv/bin/activate`
5.  Install the PyPI modules you'll need to a lib folder: `pip install -t src/lib -r requirements.txt`
6.  Set up a [Monzo Client application](https://developers.monzo.com/apps/home)
7.  Deploy a version of the code to AppEngine to set it up for first run: `cd src && gcloud app deploy`
8.  Add the Client ID and Secret to your [project DataStore](https://console.cloud.google.com/datastore/) as `MONZO_CLIENT_ID` and `MONZO_CLIENT_SECRET` - if you go through the oauth process without this you will get errors but the two keys will be created with placeholder values, which makes it easier to add them in the right way.
9.  View logs at https://console.cloud.google.com/logs/viewer
