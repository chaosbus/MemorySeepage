# -*- coding: utf-8 -*-
import os
import re
import hashlib
import json
import datetime
import exifread
import shutil
from exifread import FIELD_TYPES

TEST_REPO_BASE = 'c:\\Users\\Joe\\Pictures\\base'

# 有效的图像文件后缀名
_POSTFIX_PHOTO_NAME_SET = ('JPG', 'JPEG', 'TIFF')

# 需要保留的
_EXIF_TAG_EXPECT = ('GPS GPSLatitudeRef',
                    'GPS GPSLatitude',
                    'GPS GPSLongitudeRef',
                    'GPS GPSLongitude',
                    'GPS GPSAltitude',
                    'Image Make',
                    'Image Model',
                    'Image DateTime',
                    'EXIF ExposureTime',
                    'EXIF FNumber',
                    'EXIF ISOSpeedRatings',
                    'EXIF FocalLength',
                    'EXIF MaxApertureValue',
                    'EXIF ExifImageWidth',
                    'EXIF ExifImageLength',
                    'EXIF FocalLengthIn35mmFilm',
                    'EXIF ExposureProgram')

# 需要处理为10进制的度
_EXIF_TAG_GPS_LOC = ('GPS GPSLongitude',
                     'GPS GPSLatitude')

# 需要处理为可常规显示的分数
_EXIF_TAG_FRACTION = ('EXIF FocalLength',
                      'EXIF ExposureTime',
                      'EXIF FNumber',
                      'EXIF ApertureValue',
                      'EXIF ShutterSpeedValue',
                      'EXIF MaxApertureValue')

# 需要转换为datetime类型的时间
_EXIF_TAG_TIME = ('Image DateTime',
                  'EXIF DateTimeOriginal',
                  'EXIF DateTimeDigitized')


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


def get_numerator_and_denominator(formula):
    """
    分离分子分母。例：xxx/yyy
    :param formula:分子/分母(字符串)
    :return:分子, 分母(float类型)
    """
    [numerator, denominator] = formula.split('/')
    return float(numerator), float(denominator)


def fix_exif_fraction(value, accuracy=0):
    """
    修正分数公式，返回通用的可读的格式(1/xxx)
    整数不作修改
    :param value:
    :param accuracy:小数点精度
    :return:
    """
    if '/' in value:
        numerator, denominator = get_numerator_and_denominator(value)
        if numerator < denominator:
            return '1/' + str(int(round(denominator / numerator, 0)))
        else:
            t = round(numerator / denominator, accuracy)
            return str(int(t)) if accuracy == 0 else str(t)
    else:
        return value


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
        return datetime.datetime.strptime(value, '%Y:%m:%d %H:%M:%S')


def fix_exif_gps_loc(value):
    """
    将坐标的度分秒转为10进制的度
    deg + min/60 + sec/3600
    :param value:
    :return:
    """
    return re.sub('\[(\d{1,3}), (\d{1,3}), (\d+)/(\d+)\]',
                  lambda x: str(
                      float(x.group(1)) + float(x.group(2)) / 60 + float(x.group(3)) / float(x.group(4)) / 3600),
                  value)


def correct_exif_info(func):
    def warp(*args, **kwargs):
        info = func(*args, **kwargs)
        if not info:
            return info

        for tag in _EXIF_TAG_FRACTION:
            if tag in info and info.get(tag):
                info[tag] = fix_exif_fraction(info.get(tag), 2)

        for tag in _EXIF_TAG_GPS_LOC:
            if tag in info and info.get(tag):
                info[tag] = fix_exif_gps_loc(info.get(tag))

        for tag in _EXIF_TAG_TIME:
            if tag in info and info.get(tag):
                info[tag] = fix_exif_date(info.get(tag))

        for tag in ('Image Copyright',):
            if tag in info and info.get(tag):
                info[tag] = info.get(tag)[:-7]
        return info

    return warp


# def exif_info_edit(info):
#     """
#     修改一些字段为可读方式
#     :param info:
#     :return:
#     """
#     for tag in _EXIF_TAG_FRACTION:
#         if tag in info and info.get(tag):
#             info[tag] = fix_exif_fraction(info.get(tag), 2)
#
#     for tag in _EXIF_TAG_GPS_LOC:
#         if tag in info and info.get(tag):
#             info[tag] = fix_exif_gps_loc(info.get(tag))
#
#     custom_dict = {}
#     for tag in _EXIF_TAG_EXPECT:
#         if tag in info and info.get(tag):
#             custom_dict[tag] = info.get(tag)
#
#     for tag in _EXIF_TAG_TIME:
#         if tag in custom_dict and custom_dict.get(tag):
#             custom_dict[tag] = fix_exif_date(custom_dict.get(tag))
#
#     return custom_dict


@correct_exif_info
def get_pic_exif(filename):
    """
    获取文件的exif信息
    :param filename:文件名
    :return:全量exif(json string，存储用)，需要使用的exif(格式化的dict)
    """
    info = {}
    try:
        with open(filename, 'rb') as f:
            tags = exifread.process_file(f, details=False)
            if not tags:
                print 'exifread failed'
                return None

            for k in tags.keys():
                v = tags[k]
                # print '0x%-4x %-30s : %s' % (v.tag, tag, v.printable)
                info[k] = v.printable.strip(' ')
    except IOError, e:
        print 'open failed', e

    return info


# def get_exif(filename):
#     """
#     获取文件的exif信息
#     :param filename:文件名
#     :return:全量exif(json string，存储用)，需要使用的exif(格式化的dict)
#     """
#     try:
#         f = open(filename, 'rb')
#     except IOError, e:
#         print 'open failed', e
#         return None, None
#
#     try:
#         tags = exifread.process_file(f, details=False)
#     except Exception, e:
#         print 'process_file failed'
#         f.close()
#         return None, None
#     finally:
#         f.close()
#
#     all_dict = {}
#
#     for k in tags.keys():
#         v = tags[k]
#         # print '0x%-4x %-30s : %s' % (v.tag, tag, v.printable)
#         all_dict[k] = v.printable.strip(' ')
#
#     custom_dict = exif_info_edit(all_dict)
#
#     return all_dict if len(all_dict) else None, custom_dict if len(custom_dict) else None


def get_pic_detail_info(filename):
    """
    获取文件所有信息：exif，md5
    :param filename:
    :return: 字典格式:{'exif': {...}, 'md5': 'xxxxxx'}
    """
    return {'exif': get_pic_exif(filename), 'md5': md5sum_file(filename)}


def scan_path_import_pic(path):
    """
    扫描导入目录下的图片文件
    :param path: 导入源路径
    :return: True/False
    """
    if not os.path.exists(path) or not os.path.isdir(path):
        print 'path not exist or not a dir'
        return False

    for ff in os.listdir(path):
        filename = path + os.sep + ff.decode('gb2312')

        if not os.path.isfile(filename) or ff.partition('.')[2].upper() not in _POSTFIX_PHOTO_NAME_SET:
            continue

        print 'filename: ', ff.decode('gb2312'), filename
        info = get_pic_detail_info(filename)

        subdir = None
        if info['exif']:
            pic_date = info['exif'].get('Image DateTime')
            if pic_date and type(pic_date) == datetime.datetime:
                subdir = pic_date.strftime('%Y%m%d')
                print subdir

        spm.import_file(filename, info['md5'], subdir)


class StorePathManager(object):
    __SUB_DIR_PIC_STORE = 'store'
    __SUB_DIR_PIC_TEMP = 'tmp'
    __SUB_DIR_PIC_PENDING = 'pending'

    def __init__(self, basepath):
        self.basepath = basepath
        self.storepath = self.basepath + os.sep + self.__SUB_DIR_PIC_STORE
        self.tmppath = self.basepath + os.sep + self.__SUB_DIR_PIC_TEMP
        self.pendingpath = self.basepath + os.sep + self.__SUB_DIR_PIC_PENDING

        if not (self.isdir_ready(self.basepath) and
                    self.isdir_ready(self.storepath) and
                    self.isdir_ready(self.tmppath) and
                    self.isdir_ready(self.pendingpath)):
            pass

    # @staticmethod
    def isdir_ready(self, path):
        """
        检查目录是否可访问，不存在创建
        :param path:
        :return:
        """
        if not os.path.exists(path):
            return self.mkdir(path)

        return True

    def mkdir(self, path):
        """
        根据文件生成日期创建子目录
        :param path:
        :return:
        """
        # date_str = date.strftime('%Y%m%d')
        # sub_path = self.basepath + os.sep + self.__SUB_DIR_PIC_STORE + os.sep + date_str
        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except OSError, e:
                print 'mkdir error'
                return False
        return True

    def import_file(self, sourcefile, basename_filename, subdir=None):
        """
        导入文件
        :param sourcefile: 源文件，带路径。eg. /path/subdir/a.jpg
        :param basename_filename: 文件名不带路径。eg. b.jpg（此处应该为md5码）
        :return:
        """
        if not (os.path.exists(sourcefile) and os.path.isfile(sourcefile)):
            return False
        if subdir:
            destfile = self.storepath + os.sep + subdir + os.sep + basename_filename
            destpath = self.storepath + os.sep + subdir
            if not os.path.exists(destpath):
                self.mkdir(destpath)
        else:
            destfile = self.pendingpath + os.sep + basename_filename

        if os.path.exists(destfile) and os.path.isfile(destfile):
            print 'file %s is exist, skip' % destfile

        print sourcefile, destfile
        shutil.copy(sourcefile, destfile)


def correct_exif_info1(func):
    def warp(*args, **kwargs):
        info = func(*args, **kwargs)
        if not info:
            return info

        for tag in _EXIF_TAG_FRACTION:
            if tag in info and info.get(tag):
                info[tag] = fix_exif_fraction(info.get(tag), 2)

        for tag in _EXIF_TAG_GPS_LOC:
            if tag in info and info.get(tag):
                info[tag] = fix_exif_gps_loc(info.get(tag))

        for tag in _EXIF_TAG_TIME:
            if tag in info and info.get(tag):
                info[tag] = fix_exif_date(info.get(tag))

        for tag in ('Image Copyright',):
            if tag in info and info.get(tag):
                info[tag] = info.get(tag)[:-7]
        return info

    return warp


_EXIF_TAG_TYPE_ASCII = ('Image Make', 'Image Model', 'EXIF DateTimeOriginal', 'Image Artist', 'Image Copyright',
                        'Image Software')

_EXIF_TAG_TYPE_INT = ('Image Orientation', 'Image ResolutionUnit', 'EXIF ExposureProgram', 'EXIF ExposureMode',
                      'EXIF ExposureMode', 'EXIF ISOSpeedRatings', 'EXIF MeteringMode', 'EXIF Flash',
                      'EXIF WhiteBalance', 'EXIF ExifImageWidth', 'EXIF ExifImageLength')

_EXIF_TAG_TYPE_RATIO = ('EXIF ExposureTime', 'EXIF FNumber', 'EXIF FocalLength')

_EXIF_TAG_TYPE_RATIO_TO_INT = ('Image XResolution', 'Image YResolution')

_EXIF_TAG_GPS_DATE = ('GPS GPSDate', 'GPS GPSTimeStamp')


def math_div_str(numerator, denominator, accuracy=0):
    if numerator < denominator:
        return '1/' + str(int(round(denominator / numerator, 0)))
    else:
        if not numerator % denominator:
            accuracy = 0
        t = round(numerator / denominator, accuracy)
        return str(int(t)) if accuracy == 0 else str(t)


def math_div(numerator, denominator, accuracy=0):
    t = round(float(numerator) / float(denominator), accuracy)
    return int(t) if accuracy == 0 else t


def fix_exif_gps_loc1(values):
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


def get_pic_exif1(filename):
    """
    获取文件的exif信息
    :param filename:文件名
    :return:全量exif(json string，存储用)，需要使用的exif(格式化的dict)
    """
    info = {}
    try:
        with open(filename, 'rb') as f:
            tags = exifread.process_file(f, details=False)
            if not tags:
                print 'exifread failed'
                return None

            tag_keys = list(tags.keys())
            tag_keys.sort()

            for k in tag_keys:
                v = tags[k]
                if k in ['JPEGThumbnail', 'TIFFThumbnail']:
                    continue

                if k in _EXIF_TAG_TYPE_ASCII and v.field_type == 2:
                    info[k] = v.values.strip(' ')

                if k in _EXIF_TAG_TYPE_INT and v.field_type in (3, 4):
                    info[k] = v.values[0] if len(v.values) else -1

                if k in _EXIF_TAG_TYPE_RATIO:
                    info[k] = math_div_str(v.values[0].num, v.values[0].den, 2)

                if k in _EXIF_TAG_TYPE_RATIO_TO_INT:
                    info[k] = math_div(v.values[0].num, v.values[0].den)

                if k in _EXIF_TAG_GPS_DATE:
                    if k == _EXIF_TAG_GPS_DATE[0]:
                        info['GPS GPSDatetime'] = v.values
                    elif k == _EXIF_TAG_GPS_DATE[1]:
                        info['GPS GPSDatetime'] += ' ' + '%.2d:%.2d:%.2d' % (math_div(v.values[0].num, v.values[0].den),
                                                                             math_div(v.values[1].num, v.values[1].den),
                                                                             math_div(v.values[2].num, v.values[2].den))
                if k in _EXIF_TAG_GPS_LOC:
                    info[k] = fix_exif_gps_loc1(v.values)

    except IOError, e:
        print 'open failed', e

    # print json.dumps(info)
    return info


if __name__ == '__main__':
    # filename = 'C:\\Users\\Joe\\Pictures\\IMG_20170401_212714.jpg'
    # a = get_pic_detail_info(filename)
    # print a
    # a, c = get_exif(filename)g
    #
    # print 'all json : ', json.dumps(a)
    #
    # print 'dict obj : ', c
    #
    # print md5sum_file('C:\\Users\\Joe\\Pictures\\IMG_20170401_212714.jpg')

    # path1 = 'C:\\Usersrs\\Joe\\Pictures'
    # scan_path_import_pic(path1)

    # spm = StorePathManager('/Users/Joe/Downloads/PIC/REPO')
    # scan_path_import_pic('/Users/Joe/Downloads/PIC/IMP')

    get_pic_exif1(r'/Users/Joe/Downloads/PIC/DSC_5803.NEF')
    # get_pic_exif1(r'/Users/Joe/Downloads/PIC/aaa.jpg')
