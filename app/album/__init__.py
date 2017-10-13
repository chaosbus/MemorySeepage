from flask import Blueprint

bp_album = Blueprint('album', __name__)

from . import views
