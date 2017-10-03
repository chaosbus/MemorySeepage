from flask import render_template, redirect, request, url_for, flash
from . import bp_about


@bp_about.route('/')
def index():
    return render_template('about/index.html')
