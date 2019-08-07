import os

import cv2
import numpy as np
# 加载图片
from PIL import Image


# 根据单位像素的文件体积比做判断
def __get_image_var_by_uv__(image_path):
    image = Image.open(image_path)
    image_size = image.size
    # 文件字节大小扩大10000倍后除以图片的宽高
    score = os.path.getsize(image_path) * 10000 / image_size[0] / image_size[1]
    return score > 150


# 获取cv2工具计算的图片质量
def __get_image_var_by_cv2__(image_path):
    image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), -1)
    img2gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    score = cv2.Laplacian(img2gray, cv2.CV_64F).var()
    return score > 50


# 获取图片质量. True 或 False
def is_good_image(image_path, simple_mode=True):
    try:
        if simple_mode:
            return __get_image_var_by_uv__(image_path)
        else:
            return __get_image_var_by_cv2__(image_path)
    except Exception:
        return 0
