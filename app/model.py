# -*- coding: utf-8 -*-
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app import login_manager


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    permission = db.Column(db.Integer)

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    signup_time = db.Column(db.DateTime())
    login_time = db.Column(db.DateTime())

    @property
    def password(self):
        raise AttributeError('Password is not readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return True

    def get_id(self):
        return unicode(self.id)


@login_manager.user_loader
def load_user(user_id):
    """
    Flasg_Login用于标识加载用户
    :param user_id:
    :return:
    """
    return User.query.get(int(user_id))


class ExifInfo(db.Model):
    __tablename__ = 'exif_info'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    signup_time = db.Column(db.DateTime())
    login_time = db.Column(db.DateTime())
    photo_file = db.relationship('PhotoFile', backref='exif_info')


class PhotoFile(db.Model):
    __tablename__ = 'photo_file'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)    # 文件名(md5)
    # jpg, png, raw, bmp
    type = db.Column(db.Integer)            # 文件类型
    store_path = db.Column(db.String(256))  # 存储路径
    md5 = db.Column(db.String(64), unique=True) # 文件md5码
    fingerprint = db.Column(db.String(32))  # 图片指纹
    import_date = db.Column(db.DateTime())  # 导入时间
    exif_id = db.Column(db.Integer, db.ForeignKey('exif_info.id'))


