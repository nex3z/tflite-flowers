import numpy as np
from PIL import Image


def preprocess(image, target_size):
    image = center_crop(image)
    image = image.resize(target_size, Image.ANTIALIAS)
    image = np.array(image, dtype=np.float32)
    image /= 255.0
    return image


def center_crop(image):
    width, height = image.size
    if width / height < 1:
        vertical_offset = int((height - width) / 2)
        crop = image.crop((0, vertical_offset, width, height - vertical_offset))
    else:
        horizontal_offset = int((width - height) / 2)
        crop = image.crop((horizontal_offset, 0, width - horizontal_offset, height))
    return crop
