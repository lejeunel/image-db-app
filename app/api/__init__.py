from flask_smorest import Blueprint
from flask import current_app

if 'DEFAULT_PAGINATION_PARAMETERS' in current_app.config:
    Blueprint.DEFAULT_PAGINATION_PARAMETERS = current_app.config['DEFAULT_PAGINATION_PARAMETERS']
