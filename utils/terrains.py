from enum import Enum

"""
Class used to indicate the type of the terrain - OBSTACLE has to be 0 so it will not brick the formula later
"""

class Terrain(Enum):
    OBSTACLE = 1
    OBSTACLE_MARGIN = 1
    GRASS = 3
    SIDEWALK = 100

    def __str__(self):
        return self.name