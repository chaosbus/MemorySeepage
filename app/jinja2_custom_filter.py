# -*- coding: utf-8 -*-


def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    return value.strftime(format)


# EXIF ExposureProgram
def exif_exposure_program_readable(value):
    dict_desc = {'1': 'Auto',
                 '2': 'Program Normal',
                 '3': 'Good'}
    return dict_desc.get(str(value), 'Unkown')


