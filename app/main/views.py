from flask import Flask, render_template, redirect, request, url_for, flash
from . import bp_main


@bp_main.route('/')
def index():
    # print '__name__', __name__
    return render_template('main/index.html')


