#!/bin/bash
rm -rf migrations
rm -rf storage.db
rm -rf wheremi_app/static/files
env/bin/python run.py db init
env/bin/python run.py db migrate
env/bin/python run.py db upgrade
