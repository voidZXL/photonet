from django.test import TestCase
from photonet.settings import IMAGE_ROOT
import os
from PIL import Image

preview_size = 600
thumb_size = 100

raw_path = os.path.join(IMAGE_ROOT, 'raw')
preview_path = os.path.join(IMAGE_ROOT, 'preview')
thumb_path = os.path.join(IMAGE_ROOT, 'thumb')

for maindir, subdir, file_name_list in os.walk(raw_path):
    for filename in file_name_list:
        path = os.path.join(maindir, filename)
        img = Image.open(path)
        w, h = img.size
        if w > h:
            preview_w = preview_size
            preview_h = h*preview_w / w

            thumb_h = thumb_size
            thumb_w = w * thumb_h / h
        else:
            preview_h = preview_size
            preview_w = w * preview_h / h

            thumb_w = thumb_size
            thumb_h = h * thumb_w / w

        preview_img = img.resize((int(preview_w), int(preview_h)), Image.ANTIALIAS)
        thumb_img = img.resize((int(thumb_w), int(thumb_h)), Image.ANTIALIAS)

        preview_dest = os.path.join(preview_path, filename)
        thumb_dest = os.path.join(thumb_path, filename)

        preview_img.save(preview_dest)
        thumb_img.save(thumb_dest)

# Create your tests here.
