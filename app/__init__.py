# -*- coding: utf-8 -*-
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup, Separator
from flask_sqlalchemy import SQLAlchemy
from config import config
from file_manager import PhotoFileManager

bootstrap = Bootstrap()
nav = Nav()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
pfm = PhotoFileManager()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    app.debug = True

    # bootstrap
    bootstrap.init_app(app)

    # navigation
    nav.register_element('top', Navbar(u'MemSeep',
                                       View(u'主页', 'main.index'),
                                       View(u'影集', 'album.index'),
                                       View(u'导入', 'importer.index'),
                                       Subgroup(u'备忘',
                                                View(u'项目一', 'album.index'),
                                                Separator(),
                                                View(u'项目二', 'album.index'),
                                                ),
                                       View(u'关于', 'about.index'),
                                       ))
    nav.init_app(app)

    # db
    db.init_app(app)

    # loginManager
    login_manager.init_app(app)

    # blueprint register
    from .main import bp_main
    app.register_blueprint(bp_main, url_prefix='/')
    from .album import bp_album
    app.register_blueprint(bp_album, url_prefix='/album')
    from .about import bp_about
    app.register_blueprint(bp_about, url_prefix='/about')
    from .file_imp import bp_imp
    app.register_blueprint(bp_imp, url_prefix='/import')

    # jinja2 filter
    from .tools import jinja2_custom_filter
    jinja2_custom_filter.init_app(app)

    pfm.init_app(app)

    app.add_url_rule('/db/<path:filename>', endpoint='database', build_only=True)

    return app

