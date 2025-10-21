import mesa
from mesa.experimental.cell_space import PropertyLayer
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

    def get_sidewalk_cords(self):
        for x in range(6, 9):
            for y in range(3, 21):
                self.sidewalk_coords.append((x, y))

        for y in range(6, 9):
            for x in range(5, 16):
                self.sidewalk_coords.append((x, y))

    def create(self):
        self.get_sidewalk_cords()
        terrain_layer = PropertyLayer(
            "sidewalk", (self.width, self.height), default_value=False, dtype=bool
        )

        for x, y in self.sidewalk_coords:
            terrain_layer.data[x, y] = True

        self.sidewalk_layer = terrain_layer
        return terrain_layer
