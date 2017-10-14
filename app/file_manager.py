# -*- coding: utf-8 -*-
import os
import shutil
# from .file_oper import create_thumb_photo


def isdir_ready(path):
    """
    检查目录是否可访问，不存在创建
    :param path:
    :return:
    """
    if not os.path.exists(path):
        return mkdir(path)

    return True


def mkdir(path):
    """
    根据文件生成日期创建子目录
    :param path:
    :return:
    """
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError, e:
            print 'mkdir error'
            return False
    return True


class PhotoFileManager:
    DATABASE = 'database'
    THUMB = 'thumb'
    TEMP = 'temp'

    def __init__(self, app=None):
        self.base_path = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.base_path = app.config['PHOTO_STORE_PATH']

    def store_file(self, src_file, dst_filename, subdir=TEMP):
        """
        导入并存储文件
        :param src_file: 源文件名，全路径。eg. /home/user/1.jpg
        :param dst_filename: 目标文件名，纯文件名不包含路径。eg. 2.jpg
        :param subdir: 目标文件存储的子目录
        :return:
        """
        if not (os.path.exists(src_file) and os.path.isfile(src_file)):
            return False

        dst_path = self.base_path + os.sep + self.DATABASE + os.sep + subdir
        dst_file = dst_path + os.sep + dst_filename

        if not os.path.exists(dst_path):
            mkdir(dst_path)

        if os.path.exists(dst_file) and os.path.isfile(dst_file):
            print 'file %s is exist, skip' % dst_file
            return True

        print src_file, dst_file
        shutil.copy(src_file, dst_file)

    def delete_file(self, src_file):
        pass


if __name__ == '__main__':
    PHOTO_STORE_PATH = '/Users/Joe/PHOTO'
    pfm = PhotoFileManager(PHOTO_STORE_PATH)

    pfm.store_file('/Users/Joe/Downloads/PIC/aaa.jpg', 'bbb.jpg')




