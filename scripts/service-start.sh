#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
source .venv/bin/activate
gunicorn -w 2 "faro_api:app().wsgi_app"
