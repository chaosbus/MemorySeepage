from flask import Blueprint

bp_imp = Blueprint('importer', __name__)

from . import views
