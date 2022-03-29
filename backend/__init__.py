import os

from celery import Celery
from flask import Flask, g
from flask_cors import CORS

from backend import celery_config
from backend.extensions import logger
from backend.utilities import load_blueprints, load_configuration
from backend import routes


def create_app(env='local'):
    # Create app
    app_instance = Flask(__name__)

    # Enable CORS
    CORS(app_instance,
         resources={r'/*': {'origins': ['http://localhost:3001',
                                        'http://localhost:3000',
                                        'http://localhost',
                                        'http://127.0.0.1',
                                        'http://127.0.0.1:3000']}},
         supports_credentials=True)

    @app_instance.before_request
    def before_request():
        g.user = None

    # Load our default configuration
    load_configuration(app_instance, env)

    # Load blueprints
    load_blueprints(app_instance)

    return app_instance


def make_celery(app_instance):
    celery_obj = Celery(
        app_instance.import_name,
        backend=app_instance.config['CELERY_RESULT_BACKEND'],
        broker=app_instance.config['CELERY_BROKER_URL']
    )
    celery_obj.conf.update(app_instance.config)
    celery_obj.config_from_object(celery_config.__name__)

    class ContextTask(celery_obj.Task):
        def __call__(self, *args, **kwargs):
            with app_instance.app_context():
                return self.run(*args, **kwargs)

    celery_obj.Task = ContextTask
    return celery_obj


settings_env = os.environ.get('ENV') or 'local'
app = create_app(settings_env)

celery = make_celery(app)

from backend.celery_tasks import *
