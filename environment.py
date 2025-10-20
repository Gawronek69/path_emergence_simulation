import mesa
from cell import Cell

"""
Class that represents the environment where agents interact
"""


class Environment():

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def create(self, model):
        pass

class TestEnvironment(Environment):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.sidewalk_coords = None

    def create(self,model):
        for x in range(self.width):
            for y in range(self.height):
                cell_type = 0  # treating 0 as grass
                cell = Cell(f"Cell_{x}_{y}", model, cell_type)
                model.grid.place_agent(cell, (x, y))

        self.sidewalk_coords = [(7, y) for y in range(3, 20)] + [(x, 7) for x in range(5, 15)]

        for x, y in self.sidewalk_coords:
            cell = model.grid.get_cell_list_contents([(x, y)])[0]
            cell.cell_type = 1 #treating 1 as sidewalk
