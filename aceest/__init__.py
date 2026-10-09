"""ACEest Fitness & Gym application package.

This file exposes the application factory used by ``app.py`` and by the test
suite. Keeping the factory here allows different configurations (dev, test,
prod) to be created on demand, which is the foundation of the CI/CD pipeline.
"""

from __future__ import annotations

import os

from flask import Flask

from . import db
from .routes.api import api_bp
from .routes.views import views_bp

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def create_app(config_object: str = "config.Config") -> Flask:
    """Create and configure a Flask application instance.

    Args:
        config_object: Dotted path to the configuration class to load.

    Returns:
        A fully configured :class:`flask.Flask` application.
    """

    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "templates"),
        static_folder=os.path.join(BASE_DIR, "static"),
    )
    app.config.from_object(config_object)

    db.init_app(app)

    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    with app.app_context():
        db.init_db()

    return app
