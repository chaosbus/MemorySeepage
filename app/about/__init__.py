from flask import Blueprint

bp_about = Blueprint('about', __name__)

from . import views
