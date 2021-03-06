# -*- coding: utf-8 -*-
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from . import login_manager


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

    #############
    # EXIF INFO #
    #############

    # ifd0
    make = db.Column(db.String(64))             # 制造商
    model = db.Column(db.String(64))            # 型号
    orientation = db.Column(db.Integer)         # 方向
    date_original = db.Column(db.DateTime())    # 拍摄时间
    x_resolution = db.Column(db.Integer())      # 水平分辨率
    y_resolution = db.Column(db.Integer())      # 垂直分辨率
    resolution_unit = db.Column(db.Integer())   # 分辨率单位
    artist = db.Column(db.String(64))           # 作者
    copyright = db.Column(db.String(64))        # 版权
    software = db.Column(db.String(10))         # 软件
    img_length = db.Column(db.Integer())        # 图片长度
    img_width = db.Column(db.Integer())         # 图片长度

    # exif ifd
    exposure_time = db.Column(db.String(8))     # 曝光时间
    exposure_program = db.Column(db.Integer())  # 曝光程序
    exposure_bias = db.Column(db.String(6))     # 曝光补偿
    exposure_mode = db.Column(db.Integer())     # 曝光模式
    fnumber = db.Column(db.String(6))           # 光圈
    sensitivity = db.Column(db.Integer())       # ISO
    metering_mode = db.Column(db.Integer())     # 测光模式
    flash = db.Column(db.Integer())             # 闪光灯
    focal_len = db.Column(db.String(8))         # 焦距
    white_balance = db.Column(db.Integer())     # 白平衡

    # gps
    # have_gps = db.Column(db.Boolean, default=False)
    gps_latitude_ref = db.Column(db.String(2))  # 经度ref
    gps_latitude = db.Column(db.Float())        # 经度
    gps_longitude_ref = db.Column(db.String(2)) # 纬度ref
    gps_longitude = db.Column(db.Float())       # 纬度
    gps_altitude = db.Column(db.Float())        # 海拔
    gps_datetime = db.Column(db.DateTime())     # gps时间
    gps_direction = db.Column(db.String(8))     # gps朝向
    gps_pos_err = db.Column(db.Integer())       # gps水平定位误差

    # foreign key。从表
    photo_id = db.Column(db.Integer, db.ForeignKey('photo_file.id'))

    def __repr__(self):
        return '<ExifInfo %r>' % self.id


class PhotoFile(db.Model):
    __tablename__ = 'photo_file'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)                 # 文件名(md5码，唯一性)
    postfix = db.Column(db.String(8), nullable=False)               # 文件后缀名（导出文件用）
    size = db.Column(db.Integer())                                  # 文件大小byte
    store_path = db.Column(db.String(256), nullable=False)          # 存储路径

    type = db.Column(db.String(8))                                  # 文件真实类型[jpeg, png, tiff, gif]
    md5 = db.Column(db.String(32), unique=True)                     # 文件md5码
    fingerprint = db.Column(db.String(32))                          # 图片指纹
    import_date = db.Column(db.DateTime(), default=datetime.now())  # 导入时间
    modify_date = db.Column(db.DateTime())                          # 最近修改时间

    # description = db.Column(db.Text())                              # 描述

    exif = db.relationship('ExifInfo', uselist=False, backref='photo_file')  #, cascade='save-update, delete')
    # album = db.relationship('PhotoAlbum', backref='photo_file')

    def __repr__(self):
        return '<PhotoFile %r.%r>' % (self.name, self.postfix)


class PhotoAlbum(db.Model):
    __tablename__ = 'photo_album'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)    # 图片集名
    desc = db.Column(db.String(512), unique=True)   # 图片集描述

    def __repr__(self):
        return '<PhotoAlbum %r>' % self.name

