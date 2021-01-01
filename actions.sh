#!/usr/bin/env bash

if [ $1 == "deploy" ]
then
    gcloud app deploy 
    gcloud app browse
fi

if [ $1 == "run" ]
then
    gunicorn -b 0.0.0.0:8000 main:app
fi

if [ $1 == "debug" ]
then
    export FLASK_APP=main.py
    export FLASK_ENV=development
    flask run --host=0.0.0.0
fi