"""Event Attestator API package"""

import logging
import os
import secrets

import flask

from .views import root_view


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__package__)

CLIENT_CONFIG_ENV = "ATTESTATOR_CLIENT_CONFIG"
if (CLIENT_CONFIG := os.environ.get(CLIENT_CONFIG_ENV)) is not None:
    logger.info("using %s: %s", CLIENT_CONFIG_ENV, CLIENT_CONFIG)
else:
    logger.info("%s not set, using client defaults", CLIENT_CONFIG_ENV)
    CLIENT_CONFIG = ""

api_app = flask.Flask(__package__)
api_app.config["SECRET_KEY"] = secrets.token_hex()
api_app.config["client"] = CLIENT_CONFIG
api_app.add_url_rule("/", view_func=root_view, methods=("POST",))
