import mesa
from mesa.experimental.cell_space import PropertyLayer
from utils import images
"""
Class that represents the environment where agents interact
"""

class Environment:

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def create(self):
        pass

class TestEnvironment(Environment):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.sidewalk_coords = []
        self.sidewalk_layer = None
        self.obstacle_coords = []
        self.obstacle_layer = None

    def get_sidewalk_cords(self):
        coords = images.get_coordinates("doria_pamphil")

        for x in range(100):
            for y in range(100):
                if coords[x, y] == 1:
                    self.sidewalk_coords.append((x, y))

    def get_obstacles_cords(self):
        coords = images.get_coordinates("doria_pamphil")

        for x in range(100):
            for y in range(100):
                if coords[x, y] == 2:
                    self.obstacle_coords.append((y, x))


    def create(self):
        self.get_sidewalk_cords()
        terrain_layer = PropertyLayer(
            "sidewalk", (self.width, self.height), default_value=False, dtype=bool
        )

        self.get_obstacles_cords()
        obstacle_layer = PropertyLayer(
            "obstacles", (self.width, self.height), default_value=False, dtype=bool
        )

        for x, y in self.sidewalk_coords:
            terrain_layer.data[x, y] = True

        for x, y in self.obstacle_coords:
            obstacle_layer.data[x, y] = True

        self.sidewalk_layer = terrain_layer
        self.obstacle_layer = obstacle_layer

        return [terrain_layer, obstacle_layer]
