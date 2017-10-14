# -*- coding: utf-8 -*-
import os
import shutil
import fnmatch
import hashlib
from datetime import datetime
import PIL
from PIL import Image
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


def math_div_str(numerator, denominator, accuracy=0, no_div=False):
    """
    除法
    :param numerator: 分子
    :param denominator: 分母
    :param accuracy: 小数点精度
    :param no_div: 是否需要除。如3/5，True为3/5，False为1/1.6
    :return:
    """
    if denominator == 0 or numerator == 0:
        return 0
    if abs(numerator) < abs(denominator):
        if no_div:
            return '%d/%d' % (numerator, denominator)
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
                          float(math_div(sec.num, sec.den)) / 3600), 9)
        return loc


def fix_exif_date(value):
    """
    将时间字符串转换为datetime
    :param value:
    :return:
    """
    # FIXME 严格应该做正则判断
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
                info[k] = math_div_str(v.values[0].num, v.values[0].den, 0 if k in ("EXIF FocalLength",) else 2,
                                       True if k in ('EXIF ExposureBiasValue',) else False)

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
    :return: 字典格式 {'exif': {...}, 'file': {...}}
    """
    return {'exif': get_pic_exif(filename),
            'file': {'md5': md5sum_file(filename),
                     'imgtype': detect_image_type(filename),
                     'postfix': get_file_postfix(os.path.splitext(os.path.basename(filename))[1][1:]).upper(),
                     'size': os.path.getsize(filename)
                     }
            }


def find_files(root, patterns='*', folder_on_find=False):
    """
    查询文件
    :param root: 根路径
    :param patterns: 正则匹配，多条件用';'分隔。如'*.jpg;*.gif;*.png'
    :param folder_on_find: 是否对目录匹配
    :return:
    """
    patterns = patterns.split(';')

    for path, subdirs, files in os.walk(root):
        if folder_on_find:
            files.extend(subdirs)
        files.sort()

        for name in files:
            for pattern in patterns:
                if fnmatch.fnmatch(name.upper(), pattern.upper()):
                    yield os.path.join(path, name)
                    break


def create_thumb_photo(src_filename, dst_filename='', base_size=300, base_on_width=True, self_adopter=False, quality=100):
    """
    图片裁剪
    :param src_filename: 文件名，物理路径
    :param dst_filename: 文件名，物理路径
    :param base_size: 裁剪尺寸
    :param base_on_width: 默认以宽为准。False以长为准
    :param self_adopter: 自适应。以长/宽中最短的基于base_size裁剪
    :return:
    """

    img = Image.open(src_filename)
    width = img.size[0]
    length = img.size[1]

    ratio = float(width) / float(length)
    print 'I :', width, ' / ', length, ' = ', float(width) / length

    if self_adopter:
        shortter = width < length
        if base_on_width:
            e_width = base_size if shortter else int(round(base_size * ratio))
        else:
            e_width = int(round(base_size * ratio)) if shortter else base_size
    else:
        e_width = base_size if base_on_width else int(round(base_size * ratio))

    e_length = int(round(e_width / ratio))
    print 'II:', e_width, ' / ', e_length, ' = ', float(e_width) / e_length
    print '='*20

    img1 = img.resize((e_width, e_length), PIL.Image.ANTIALIAS)
    img1.save(dst_filename, quality=quality)


if __name__ == '__main__':
    y = find_files(r'C:\Users\Joe\svn_workspace\dhmp_if\HOME_NGX\nginx\conf', '*.lua')
    for x in y:
        print x

    p1 = r'/Users/Joe/Downloads/PIC/aaa.jpg'
    p2 = r'/Users/Joe/Downloads/PIC/DSC_5803.NEF'
    # p3 = r'C:\Users\Joe\Downloads\IMG_20170416_104328.jpg'
    # p4 = r'C:\Users\Joe\Pictures\DSC_5519.NEF'
    # p5 = r'C:\Users\Joe\Pictures\DSC_4895.jpg'
    # get_pic_exif(p1)
    # get_pic_exif(p2)
    # print get_pic_detail_info(p5)
    # print get_pic_detail_info(p2)


