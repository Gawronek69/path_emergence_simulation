"""
Function used for preprocessing images - creating grid coordinators
"""

import cv2
import numpy as np

def get_coordinates(image):
    images = {"doria_pamphil": "utils/park_imgs/doria_pamphil.png"}

    try:
        path = images[image]
    except KeyError:
        print("Image " + image + " not found!")
        return None

    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    img = img.astype('uint8')
    img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

    coords = np.zeros((100, 100))

    for i in range(100):
        for j in range(100):
            if img[i, j] >= 151:
                coords[i, j] = 0
            elif 146 <= img[i, j] <= 150:
                coords[i, j] = 1
            else:
                coords[i, j] = 2

    return coords.astype('uint8')