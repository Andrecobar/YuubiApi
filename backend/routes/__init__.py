from flask import Blueprint

movies_bp = Blueprint('movies', __name__)
series_bp = Blueprint('series', __name__)
admin_bp = Blueprint('admin', __name__)

from . import movies, series, admin
