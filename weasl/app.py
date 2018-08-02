# -*- coding: utf-8 -*-
"""The app module, containing the app factory function."""
from flask import Flask, jsonify
from flask_cors import CORS
from marshmallow.exceptions import ValidationError
from twilio.rest import Client

from weasl import commands
from weasl.errors import APIException
from weasl.extensions import db, migrate
from weasl.settings import ProdConfig
from weasl.user.models import EmailToken, SMSToken, User
from weasl.org.models import Org
from weasl.end_user.models import EndUser


def create_app(config_object=ProdConfig):
    """This function is an application factory.

    As explained here: http://flask.pocoo.org/docs/patterns/appfactories/.

    :param config_object: The configuration object to use.
    """
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)
    app.twilio_client = Client(
        config_object.TWILIO_ACCOUNT_SID,
        config_object.TWILIO_AUTH_TOKEN,
    )
    register_blueprints(app)
    register_extensions(app)
    register_errorhandlers(app)
    register_shellcontext(app)
    register_commands(app)

    return app


def register_extensions(app):
    """Register Flask extensions."""
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    return None


def register_blueprints(app):
    """Register Flask blueprints."""
    from weasl.api.auth import blueprint as auth_blueprint
    from weasl.api.users import blueprint as users_blueprint
    from weasl.api.orgs import blueprint as orgs_blueprint
    from weasl.api.end_users import blueprint as end_users_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(users_blueprint)
    app.register_blueprint(orgs_blueprint)
    app.register_blueprint(end_users_blueprint)
    return None


def register_errorhandlers(app):
    """Register error handlers."""
    @app.errorhandler(ValidationError)
    def handle_marshmallow_validation_error(ex):
        response = jsonify(error_code="data-validation-error",
                           error_message=ex.messages.get(('_schema')))
        response.status_code = 422
        return response

    @app.errorhandler(APIException)
    def handle_api_error(err):
        """Handle an APIException."""
        return jsonify(err.to_dict()), err.status_code

    @app.errorhandler(404)
    def handle_404_error(err):
        """Handle a 404."""
        return jsonify(
            error_code="not-found",
            error_message="Could not find the specified resource."
        ), 404

    return None


def register_shellcontext(app):
    """Register shell context objects."""
    def shell_context():
        """Shell context objects."""
        return {'db': db}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)
    app.cli.add_command(commands.clean)
    app.cli.add_command(commands.urls)
