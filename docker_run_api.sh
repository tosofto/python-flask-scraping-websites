#!/bin/bash
NAME="backend-api" # Name of the application
PROJECT_DIR=/app
NUM_WORKERS=2
SOCK_FILE=/gunicorn.sock # we will communicate using this unix socket
USER=root
FLASK_APP=runserver # WSGI module name
FLASK_SOCKET=gevent
echo "Starting $NAME as $(whoami)"

# Activate the virtual environment
cd $PROJECT_DIR || exit
export PYTHONPATH=$PROJECT_DIR:$PYTHONPATH
# set environment variables
export ENV="docker"

RUNDIR=$(dirname $SOCK_FILE)
test -d "$RUNDIR" || mkdir -p "$RUNDIR"

# Start gunicorn server
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec gunicorn -k ${FLASK_SOCKET} ${FLASK_APP}:app --workers ${NUM_WORKERS} --worker-connections 1000 -p runserver.pid -b 0.0.0.0:5000 --timeout 3000 --reload
