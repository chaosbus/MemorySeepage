# -*- coding: utf-8 -*-
from PIL import Image
import os
import PIL

def create_thumbnail(image):
    ff = os.path.basename(image)
    filename, ext = os.path.splitext(ff)
    base_width = 300
    img = Image.open(image)  # # 从上传集获取path

    tname = filename + '_300' + ext

    # if img.size[0] <= 300:  # 如果图片宽度小于300，不作处理
    #     return photos.url(image)  # 从上传集获取url
    w_percent = (base_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)
    img.save(r'/Users/Joe/PIC/thumb/' + filename + '_300' + '.jpg')
    # return url_for('.uploaded_file', filename=filename + '_t' + ext)


if __name__ == '__main__':
    p1 = '/Users/Joe/PIC/DSC_5606.jpg'
    p2 = '/Users/Joe/PIC/DSC_5084.NEF'
    # create_thumbnail(p1)
    # create_thumbnail(p2)

    create_thumb_photo(p1, p1 + 'test1.jpg', base_size=500)
    create_thumb_photo(p1, p1 + 'test2.jpg', base_size=500, base_on_width=False)
    # create_thumb_photo(src_filename=p2, base_size=500)

