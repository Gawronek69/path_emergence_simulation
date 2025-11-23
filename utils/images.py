"""
Function used for preprocessing images - creating grid coordinators
"""

import cv2
import numpy as np
from utils.terrains import Terrain

images = {"doria_pamphil": "utils/park_imgs/doria_pamphil.png",
              "doria_pamphil_west": "utils/park_imgs/doria_pamphil_west.png",
              "greenwich": "utils/park_imgs/greenwich.png",
              "blackheath": "utils/park_imgs/blackheath.png",
              "hyde": "utils/park_imgs/hyde.png",
              "richmond": "utils/park_imgs/richmond.png",
              "clapham": "utils/park_imgs/clapham.png",
              "hampstead": "utils/park_imgs/hampstead.png"}

def get_coordinates(image):
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
                coords[i, j] = Terrain.GRASS.value # value for grass
            elif 146 <= img[i, j] <= 150:
                coords[i, j] = Terrain.SIDEWALK.value # value for sidewalk
            else:
                coords[i, j] = Terrain.OBSTACLE.value # value for obstacles


    return coords.astype('uint8')


def binarize_desired_paths(path, name):
    try:
        img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    except Exception as e:
        print("Error when preprocessing file " + path + ": " + str(e))
        return -1

    img = cv2.resize(img, (100, 100), interpolation=cv2.INTER_BITS)

    binary = (img > 200).astype('uint8')

    np.save(f"{name}.npy", binary)

    # use np.load to get 0/1 values for each park representing desired paths
    # loaded = np.load("array.npy")