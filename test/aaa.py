# -*- coding: utf-8 -*-
import os
import hashlib
import json
from datetime import datetime
import imghdr
import exifread


def md5sum_string(string):
    """
    计算字符串的md5
    :param string:
    :return:
    """
    md5obj = hashlib.md5()
    md5obj.update(string)
    return md5obj.hexdigest()


def md5sum_file(filename):
    """
    计算文件的md5
    :param filename:
    :return:
    """
    if not os.path.isfile(filename):
        return None
    try:
        with open(filename, 'rb') as f:
            md5obj = hashlib.md5()
            while True:
                b = f.read(8096)
                if not b:
                    break
                md5obj.update(b)
                return md5obj.hexdigest()
    except IOError, e:
        return None


def detect_image_type(filename):
    """
    获取图像文件类型
    :param filename:
    :return: jpge|png|gif|tiff等。失败返回None
    """
    return imghdr.what(filename)


def math_div_str(numerator, denominator, accuracy=0):
    """
    除法
    :param numerator:
    :param denominator:
    :param accuracy:
    :return:
    """
    if denominator == 0 or numerator == 0:
        return 0
    if abs(numerator) < abs(denominator):
        return '1/' + str(int(round(denominator / numerator, 0)))
    else:
        if not numerator % denominator:
            accuracy = 0
        t = round(float(numerator) / float(denominator), accuracy)
        return str(int(t)) if accuracy == 0 else str(t)


def math_div(numerator, denominator, accuracy=0):
    """
    除法
    :param numerator:
    :param denominator:
    :param accuracy:
    :return:
    """
    if denominator == 0:
        return 0
    t = round(float(numerator) / float(denominator), accuracy)
    return int(t) if accuracy == 0 else t


def fix_exif_gps_loc(values):
    """
    将坐标的度分秒转为10进制的度
    deg + min/60 + sec/3600
    :param values:
    :return:
    """
    if isinstance(values, list) and len(values) == 3:
        deg = values[0]
        min = values[1]
        sec = values[2]
        loc = round(float(math_div(deg.num, deg.den) +
                          float(math_div(min.num, min.den)) / 60 +
                          float(math_div(sec.num, sec.den)) / 3600), 6)
        return loc


def fix_exif_date(value):
    """
    将时间字符串转换为datetime
    :param value:
    :return:
    """
    if len(value) != 19:
        print 'not format [%Y:%m:%d %H:%M:%S]'
        return None
    else:
        return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')


# 转为string类型
_EXIF_TAG_TYPE_ASCII = ('Image Make', 'Image Model', 'EXIF DateTimeOriginal', 'Image Artist', 'Image Copyright',
                        'Image Software', 'GPS GPSLongitudeRef', 'GPS GPSLatitudeRef')

# 转为int类型
_EXIF_TAG_TYPE_INT = ('Image Orientation', 'Image ResolutionUnit', 'EXIF ExposureProgram', 'EXIF ExposureMode',
                      'EXIF ExposureMode', 'EXIF ISOSpeedRatings', 'EXIF MeteringMode', 'EXIF Flash',
                      'EXIF WhiteBalance', 'EXIF ExifImageWidth', 'EXIF ExifImageLength')

# 转为可读化的string类型。'EXIF FocalLength'取整
_EXIF_TAG_TYPE_RATIO = ('EXIF ExposureTime', 'EXIF FNumber', 'EXIF FocalLength', 'EXIF ExposureBiasValue')

# 转为整形
_EXIF_TAG_TYPE_RATIO_TO_INT = ('Image XResolution', 'Image YResolution', 'GPS GPSAltitude')

# 将date与time合并为yyyy-mm-dd hh24:mi:ss
_EXIF_TAG_GPS_DATE = ('GPS GPSDate', 'GPS GPSTimeStamp')

# 转为float类型。将gps坐标处理为10进制的度
_EXIF_TAG_GPS_LOC = ('GPS GPSLongitude', 'GPS GPSLatitude')


def correct_exif_info(func):
    """
    decorator. 生成需要的信息
    :param func:
    :return: dict
    """

    def warp(*args, **kwargs):
        tags = func(*args, **kwargs)
        if not tags:
            return tags

        info = {}
        tag_keys = list(tags.keys())
        tag_keys.sort()

        for k in tag_keys:
            v = tags[k]
            # print k, v.values
            if k in ['JPEGThumbnail', 'TIFFThumbnail']:
                continue

            if k in _EXIF_TAG_TYPE_ASCII and v.field_type == 2:
                info[k] = v.values.strip(' ')

            if k in _EXIF_TAG_TYPE_INT and v.field_type in (3, 4):
                info[k] = v.values[0] if len(v.values) else -99

            if k in _EXIF_TAG_TYPE_RATIO and v.field_type in (5, 10):
                info[k] = math_div_str(v.values[0].num, v.values[0].den, 0 if k in ("EXIF FocalLength",) else 2)

            if k in _EXIF_TAG_TYPE_RATIO_TO_INT and v.field_type in (5, 10):
                info[k] = math_div(v.values[0].num, v.values[0].den)

            if k in _EXIF_TAG_GPS_DATE:
                if k == _EXIF_TAG_GPS_DATE[0]:
                    info['GPS GPSDatetime'] = v.values
                elif k == _EXIF_TAG_GPS_DATE[1]:
                    info['GPS GPSDatetime'] += ' ' + '%.2d:%.2d:%.2d' % (math_div(v.values[0].num, v.values[0].den),
                                                                         math_div(v.values[1].num, v.values[1].den),
                                                                         math_div(v.values[2].num, v.values[2].den))
            if k in _EXIF_TAG_GPS_LOC:
                info[k] = fix_exif_gps_loc(v.values)

        if 'GPS GPSDatetime' in info.keys():
            info['GPS GPSDatetime'] = fix_exif_date(info['GPS GPSDatetime'])
        if 'EXIF DateTimeOriginal' in info.keys():
            info['EXIF DateTimeOriginal'] = fix_exif_date(info['EXIF DateTimeOriginal'])

        del tags
        return info

    return warp


@correct_exif_info
def get_pic_exif(filename):
    """
    获取文件的exif信息
    :param filename:文件名
    :return:全量exif(json string，存储用)，需要使用的exif(格式化的dict)
    """
    # info = {}
    try:
        with open(filename, 'rb') as f:
            tags = exifread.process_file(f, details=False)
            if not tags:
                print 'exifread failed'
                return None
    except IOError, e:
        print 'open failed', e

    # print json.dumps(info)
    return tags


get_file_postfix = lambda i: i if i else 'undef'


def get_pic_detail_info(filename):
    """
    获取文件所有信息：exif，md5
    :param filename:
    :return: 字典格式:{'exif': {...}, 'md5': 'xxxxxx'}
    """
    return {'exif': get_pic_exif(filename),
            'file': {'md5': md5sum_file(filename),
                     'imgtype': detect_image_type(filename),
                     'postfix': get_file_postfix(os.path.splitext(os.path.basename(filename))[1])}}


from app.models import ExifInfo, PhotoFile


def insert_photo_file(info):
    record = PhotoFile(name=info.get('md5'),
                       postfix=info.get('postfix'),
                       type=info.get('imgtype'),
                       md5=info.get('md5'),
                       store_path=info.get('md5'),  # FIXME
                       fingerprint=info.get('NULL')
                       # import_date=datetime.now(),
                       # modify_date=datetime.now()
                       )
    return record


def insert_exif_info(info):
    record = ExifInfo(make=info.get('Image Make'),
                      model=info.get('Image Model'),
                      orientation=info.get('Image Orientation'),
                      date_original=info.get('EXIF DateTimeOriginal'),
                      x_resolution=info.get('Image XResolution'),
                      y_resolution=info.get('Image YResolution'),
                      resolution_unit=info.get('Image ResolutionUnit'),
                      artist=info.get('Image Artist'),
                      copyright=info.get('Image Copyright'),
                      software=info.get('Image Software'),
                      img_length=info.get('EXIF ExifImageLength'),
                      img_width=info.get('EXIF ExifImageWidth'),
                      exposure_time=info.get('EXIF ExposureTime'),
                      exposure_program=info.get('EXIF ExposureProgram'),
                      exposure_bias=info.get('EXIF ExposureBiasValue'),
                      exposure_mode=info.get('EXIF ExposureMode'),
                      fnumber=info.get('EXIF FNumber'),
                      sensitivity=info.get('EXIF ISOSpeedRatings'),
                      metering_mode=info.get('EXIF MeteringMode'),
                      flash=info.get('EXIF Flash'),
                      focal_len=info.get('EXIF FocalLength'),
                      white_balance=info.get('EXIF WhiteBalance'),
                      gps_latitude_ref=info.get('GPS GPSLatitudeRef'),
                      gps_latitude=info.get('GPS GPSLatitude'),
                      gps_longitude_ref=info.get('GPS GPSLongitudeRef'),
                      gps_longitude=info.get('GPS GPSLongitude'),
                      gps_altitude=info.get('GPS GPSAltitude'),
                      gps_datetime=info.get('GPS GPSDatetime'),
                      gps_direction=info.get(''),
                      gps_pos_err=info.get(''))
    return record


def add_new_photo(info):
    info_file = info.get('file')
    info_exif = info.get('exif')

    record = PhotoFile(name=info_file.get('md5'),
                       postfix=info_file.get('postfix'),
                       type=info_file.get('imgtype'),
                       md5=info_file.get('md5'),
                       store_path=info_file.get('md5'), # FIXME 临时
                       fingerprint=info_file.get('NULL')
                       # import_date=datetime.now(),
                       # modify_date=datetime.now()
                       )

    if info_exif:
        record.exif = add_new_exif(info_exif)

    return record


def add_new_exif(info):
    return ExifInfo(make=info.get('Image Make'),
                    model=info.get('Image Model'),
                    orientation=info.get('Image Orientation'),
                    date_original=info.get('EXIF DateTimeOriginal'),
                    x_resolution=info.get('Image XResolution'),
                    y_resolution=info.get('Image YResolution'),
                    resolution_unit=info.get('Image ResolutionUnit'),
                    artist=info.get('Image Artist'),
                    copyright=info.get('Image Copyright'),
                    software=info.get('Image Software'),
                    img_length=info.get('EXIF ExifImageLength'),
                    img_width=info.get('EXIF ExifImageWidth'),
                    exposure_time=info.get('EXIF ExposureTime'),
                    exposure_program=info.get('EXIF ExposureProgram'),
                    exposure_bias=info.get('EXIF ExposureBiasValue'),
                    exposure_mode=info.get('EXIF ExposureMode'),
                    fnumber=info.get('EXIF FNumber'),
                    sensitivity=info.get('EXIF ISOSpeedRatings'),
                    metering_mode=info.get('EXIF MeteringMode'),
                    flash=info.get('EXIF Flash'),
                    focal_len=info.get('EXIF FocalLength'),
                    white_balance=info.get('EXIF WhiteBalance'),
                    gps_latitude_ref=info.get('GPS GPSLatitudeRef'),
                    gps_latitude=info.get('GPS GPSLatitude'),
                    gps_longitude_ref=info.get('GPS GPSLongitudeRef'),
                    gps_longitude=info.get('GPS GPSLongitude'),
                    gps_altitude=info.get('GPS GPSAltitude'),
                    gps_datetime=info.get('GPS GPSDatetime'),
                    gps_direction=info.get(''),
                    gps_pos_err=info.get(''))


if __name__ == '__main__':
    p1 = r'/Users/Joe/Downloads/PIC/aaa.jpg'
    p2 = r'/Users/Joe/Downloads/PIC/DSC_5803.NEF'
    p3 = r'C:\Users\Joe\Downloads\IMG_20170416_104328.jpg'
    p4 = r'C:\Users\Joe\Pictures\DSC_5519.NEF'
    p5 = r'C:\Users\Joe\Pictures\DSC_4895.jpg'
    # get_pic_exif(p1)
    # get_pic_exif(p2)
    print get_pic_detail_info(p5)
    # print get_pic_detail_info(p2)
