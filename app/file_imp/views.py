from flask import render_template, redirect, request, url_for, flash
from . import bp_imp
from ..tools import find_files, get_pic_detail_info, add_new_photo
from .. import db


def foo():
    fs = find_files(r'/Users/Joe/PIC', '*.jpg;*.nef;*.cr2')
    for f in fs:
        print f
        i = get_pic_detail_info(f)
        print i
        db.session.add(add_new_photo(i))
        db.session.commit()

    # try:
    #     db.session.commit()
    # except Exception, e:
    #     db.session.rollback()
    #     print 'error', e


@bp_imp.route('/', methods=['GET', 'POST'])
def index():
    foo()
    return render_template('album/index.html')



