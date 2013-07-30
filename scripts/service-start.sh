#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR
source .venv/bin/activate
WORKERS=2
PORT=8000
IP=127.0.0.1
exec gunicorn -w $WORKERS -b $IP:$PORT "faro_api:app().wsgi_app"
