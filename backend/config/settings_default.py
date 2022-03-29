import os

DEBUG = True
LOGGING_LEVEL = 'logging.DEBUG'
SECRET_KEY = 'jt\x90|\xe8Wu\xc7DX-%\x93\x7f\xd9.'
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_URL = f"redis://{REDIS_HOST}:6379/0"
CELERY_RESULT_BACKEND = REDIS_URL
CELERY_BROKER_URL = REDIS_URL
