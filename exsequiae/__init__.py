from flask import Flask
from flaskext.babel import Babel, format_datetime, format_date
from storage import Storage, CacheWrapper

from application import auth, defs


def create_app(instance_path):
    app = Flask(__name__, instance_relative_config=True, instance_path=instance_path)
    app.config.from_object('exsequiae.default_config')
    app.config.from_pyfile('exsequiae.cfg')

    app.register_blueprint(auth)
    app.register_blueprint(defs)

    babel = Babel(app)

    app.jinja_env.filters['dt'] = format_datetime
    app.jinja_env.filters['d'] = format_date

    app.storage = Storage.initialize(app.config)

    return app
