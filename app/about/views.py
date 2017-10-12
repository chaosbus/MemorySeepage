from flask import render_template, redirect, request, url_for, flash
from . import bp_about
from ..models import PhotoFile, ExifInfo


@bp_about.route('/')
def index():
    a = PhotoFile.query.order_by(PhotoFile.type).all()
    return render_template('about/index.html', photos=a)

