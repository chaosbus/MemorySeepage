from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from main import bp_main
    app.register_blueprint(bp_main, url_prefix='/')

    # from api import bp_api
    # app.register_blueprint(bp_api, url_prefix='/api')
    #
    # from auth import bp_auth
    # app.register_blueprint(bp_auth, url_prefix='/auth')

    return app

