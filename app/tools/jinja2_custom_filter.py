# -*- coding: utf-8 -*-
# jinja2自定过滤器


def datetimeformat_readable(value, format='%Y-%m-%d %H:%M:%S'):
    """
    时间格式化
    :param value: datetime
    :param format:
    :return: str
    """
    if not value:
        return ''
    return value.strftime(format)


def byte_with_unit_readable(value):
    """
    将byte转为可读的单位
    :param value: 数据存储大小，int或float
    :return: 带单位的可视化大小，str
    """
    list_unit = ['Byte', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    while True:
        b = 1024 ** i
        t = float(value) / b
        if 0 < t < 1000:
            break
        i += 1

    return str(round(t, 3)) + ' ' + list_unit[i]


def exif_resolution_unit(value):
    """
    ResolutionUnit可读化
    :param value: int
    :return: description
    """
    dict_desc = {'1': 'cm',
                 '2': 'Inch',
                 '3': 'km'}
    return dict_desc.get(str(value) if isinstance(value, int) else value, '')


def exif_exposure_mode_readable(value):
    """
    ExposureMode可读化
    :param value: int
    :return: description
    """
    dict_desc = {'0': 'mode ZERO',
                 '1': 'mode A',
                 '2': 'mode B',
                 '3': 'mode C'}
    return dict_desc.get(str(value) if isinstance(value, int) else value, '')


def exif_exposure_program_readable(value):
    """
    ExposureProgram可读化
    :param value: int
    :return: description
    """
    dict_desc = {'1': 'Auto',
                 '2': 'Normal',
                 '3': 'Good',
                 '5': '555'}
    return dict_desc.get(str(value) if isinstance(value, int) else value, '')


def init_app(app):
    app.jinja_env.filters['datetimeformat'] = datetimeformat_readable
    app.jinja_env.filters['exif_ep'] = exif_exposure_program_readable
    app.jinja_env.filters['exif_em'] = exif_exposure_mode_readable
    app.jinja_env.filters['exif_ru'] = exif_resolution_unit
    app.jinja_env.filters['byte_unit'] = byte_with_unit_readable


