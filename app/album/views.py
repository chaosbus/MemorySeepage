from flask import render_template, redirect, request, url_for, flash
from . import bp_album


@bp_album.route('/', methods=['GET', 'POST'])
def index():
    return render_template('album/index.html')



