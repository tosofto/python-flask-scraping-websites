import logging

from flask import Blueprint

"""
Logging
"""
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

"""
Blueprint
"""
api = Blueprint('api', __name__)
