from flask import render_template, redirect, request, url_for, flash, current_app
from . import bp_imp
from ..tools import find_files, get_pic_detail_info, add_new_photo
from .. import db
from sqlalchemy.exc import IntegrityError
from .. import pfm


def foo():
    print current_app.config['PHOTO_STORE_PATH']
    fs = find_files(r'/Users/Joe/PIC', '*.jpg;*.nef;*.cr2')
    for f in fs:
        # print f
        i = get_pic_detail_info(f)

        md5sum = i.get('file').get('md5')
        pfm.store_file(f, md5sum, md5sum[0:2])
        # print i
        db.session.add(add_new_photo(i))
        try:
            db.session.commit()
        except IntegrityError, e:
            print 'commit %s failed' % f
            db.session.rollback()

    # try:
    #     db.session.commit()
    # except Exception, e:
    #     db.session.rollback()
    #     print 'error', e


@bp_imp.route('/', methods=['GET', 'POST'])
def index():
    foo()
    return render_template('album/index.html')



