#!/bin/bash
NAME="backend-worker" # Name of the application
PROJECT_DIR=/app
CELERY_APP=runserver # WSGI module name
echo "Starting $NAME as $(whoami)"

# Activate the virtual environment
cd $PROJECT_DIR || exit
export PYTHONPATH=$PROJECT_DIR:$PYTHONPATH

# set environment variables
export ENV="docker"

# Start worker
celery -A ${CELERY_APP}:celery worker --beat -f /var/log/celery-worker.log --loglevel=DEBUG
