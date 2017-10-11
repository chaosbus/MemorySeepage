from flask import render_template, redirect, request, url_for, flash
from . import bp_about
from ..models import PhotoFile, ExifInfo


xxx = {'2': "auto",
       '5': 'manual'}

@bp_about.route('/')
def index():
    a = PhotoFile.query.all()
    for x in a:
        print x.import_date, type(x.import_date)
    return render_template('about/index.html', photos=a, pa=xxx)

