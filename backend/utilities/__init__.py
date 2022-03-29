from backend.extensions import api


def load_configuration(app_instance, environment):
    """
    Create the file path based on the selected environment
    """
    default_configurations = 'config/settings_default.py'
    environment_configuration = 'config/settings_%s.py' % environment

    app_instance.config.from_object(__name__)
    app_instance.config.from_pyfile(default_configurations)
    app_instance.config.from_pyfile(environment_configuration)


def load_blueprints(app_instance):
    app_instance.register_blueprint(api, url_prefix='/api')
