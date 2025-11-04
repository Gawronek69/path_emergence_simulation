import mesa
from mesa.experimental.cell_space import PropertyLayer
from utils import images
from utils.terrains import Terrain
import random
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
        self.grass_coords = []
        self.grass_layer = None
        self.grass_popularity_layer = None

    def get_sidewalk_cords(self):
        coords = images.get_coordinates("hampstead")

        for x in range(100):
            for y in range(100):
                if coords[x, y] == Terrain.SIDEWALK.value:
                    self.sidewalk_coords.append((x, y))

    def get_grass_cords(self):
        coords = images.get_coordinates("hampstead")
        for x in range(100):
            for y in range(100):
                if coords[x, y] == Terrain.GRASS.value:
                    self.grass_coords.append((x, y))

    def get_obstacles_cords(self):
        coords = images.get_coordinates("hampstead")

        for x in range(100):
            for y in range(100):
                if coords[x, y] == Terrain.OBSTACLE.value:

                    self.obstacle_coords.append((x, y))


    def create(self)-> list[PropertyLayer]:
        self.get_sidewalk_cords()
        terrain_layer = PropertyLayer(
            str(Terrain.SIDEWALK), (self.width, self.height), default_value=0, dtype=int
        )

        self.get_obstacles_cords()
        obstacle_layer = PropertyLayer(
            str(Terrain.OBSTACLE), (self.width, self.height), default_value=0, dtype=int
        )

        self.get_grass_cords()
        grass_layer = PropertyLayer(
            str(Terrain.GRASS), (self.width, self.height), default_value=0, dtype=int
        )

        grass_popularity_layer = PropertyLayer(
            "GRASS_POPULARITY", (self.width, self.height), default_value=0, dtype=int
        )

        for x, y in self.sidewalk_coords:
            terrain_layer.data[x, y] = Terrain.SIDEWALK.value

        for x, y in self.obstacle_coords:
            obstacle_layer.data[x, y] = Terrain.OBSTACLE.value

        for x, y in self.grass_coords:
            grass_layer.data[x, y] = Terrain.GRASS.value
            grass_popularity_layer.data[x, y] = Terrain.GRASS.value



        self.sidewalk_layer = terrain_layer
        self.obstacle_layer = obstacle_layer
        self.grass_layer = grass_layer
        self.grass_popularity_layer = grass_popularity_layer

        return [terrain_layer, obstacle_layer, grass_layer, grass_popularity_layer]
