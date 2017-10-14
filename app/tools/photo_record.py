# -*- coding: utf-8 -*-
from datetime import datetime
from app.models import PhotoFile, ExifInfo


def add_new_photo(info):
    """
    创建图片信息记录（主表）
    :param info:
    :return:
    """
    info_file = info.get('file')
    info_exif = info.get('exif')

    record = PhotoFile(name=info_file.get('md5'),
                       postfix=info_file.get('postfix'),
                       type=info_file.get('imgtype').upper(),
                       size=info_file.get('size'),
                       md5=info_file.get('md5'),
                       store_path=info_file.get('md5')[:2],     # FIXME 临时
                       fingerprint=info_file.get('NULL'),
                       # modify_date=datetime.now()
                       import_date=datetime.now()
                       )

    if info_exif:
        record.exif = add_new_exif(info_exif)

    return record


def add_new_exif(info):
    """
    创建exif记录（从表）
    :param info:
    :return:
    """
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
    pass


