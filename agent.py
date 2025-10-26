from typing import Any

import mesa
from mesa.discrete_space import CellAgent, Cell

import numpy as np
from numpy import floating

from utils.terrains import Terrain


class ParkAgent(CellAgent):
    def __init__(self, model, cell:Cell, target: Cell):
        super().__init__(model)
        self.cell = cell
        self.target = target

    def action(self):



        curr_distance = self.curr_distance()
        print(self.cell.coordinate, self.cell.SIDEWALK)
        possible_cells = [c for c in self.cell.neighborhood if c.is_empty and (c.SIDEWALK == Terrain.SIDEWALK.value)]

        if len(possible_cells) > 0:
            self.cell = self.model.random.choice(possible_cells)



    def step(self):
        self.action()

    def calc_dest_dist(self, cell:Cell) -> floating[Any]:
        return np.linalg.norm(np.array(self.target.coordinate) - np.array(cell.coordinate))

    def curr_distance(self):
        return self.calc_dest_dist(self.cell)