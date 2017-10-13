from flask import render_template, redirect, request, url_for, flash
from . import bp_main


@bp_main.route('/')
def index():
    return render_template('main/index.html')


