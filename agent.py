import math
from typing import Any, Tuple, List

import mesa
from mesa.discrete_space import CellAgent, Cell

import numpy as np
from numpy import floating

from utils.terrains import Terrain

class ParkAgent(CellAgent):
    def __init__(self, model, cell:Cell, target: Cell, angle: int = 120, distance: int = 17, tile_weight: float = 1, distance_weight: float = 0.4):
        super().__init__(model)
        self.cell = cell
        self.target = target
        self.angle = angle
        self.distance = distance
        self.subtarget = None
        self.tile_weight = tile_weight
        self.distance_weight = distance_weight
        self.previous_cell : Cell|None = None
        self.previous_cells : List[Cell] = []


    def action(self) -> None:
        possible_cells = [c for c in self.cell.neighborhood]
        best_cells_distance  = []

        for cell in possible_cells:
            distance = ParkAgent.calc_dest_dist(cell,self.target)
            best_cells_distance.append((cell,distance))

        best_cells_distance = sorted(best_cells_distance,
                                     key=lambda c: c[1] if (c[0].OBSTACLE != Terrain.OBSTACLE.value) else math.inf)

        best_cell = best_cells_distance[0]
        if best_cell[0].SIDEWALK == Terrain.SIDEWALK.value:
            self._update_cell_parameters(best_cell[0])
        else:
            flag = False
            for cell in best_cells_distance:
                if cell[0] in self.previous_cells: pass
                if cell[0].GRASS == Terrain.GRASS.value:
                    possibility = self.random.randint(Terrain.GRASS.value,100) <= cell[0].GRASS_POPULARITY
                    if possibility:
                        self._update_cell_parameters(cell[0])
                        flag = True
                        break
                elif cell[0].SIDEWALK == Terrain.SIDEWALK.value:
                    if self.previous_cell and cell[1] < ParkAgent.calc_dest_dist(self.previous_cell,self.target):
                        self._update_cell_parameters(cell[0])
                        flag = True
                        break
            if not flag: self._update_cell_parameters(best_cell[0])


    def _update_cell_parameters(self, new_cell : Cell) -> None:
        self.previous_cell = self.cell
        self.previous_cells.append(self.cell)
        self.cell = new_cell

    """ Function that returns the visible tiles by the agent"""
    def select_subtarget(self) -> list[tuple[Cell, float]]:

        def get_cell_vec(cell1: Cell, cell2: Cell) -> np.array:
            return np.array(cell1.coordinate) - np.array(cell2.coordinate)

        def cell_in_radius(vec: np.array) -> bool:
            return (np.power(vec, 2)).sum() <= np.power(self.distance, 2)

        def cell_in_angle(vec: np.array) -> bool:
            return np.dot(vec, target_vector)/(np.linalg.norm(vec) * np.linalg.norm(target_vector)) >= np.cos(self.angle // 2)

        """Recursively starts finding candidates starting from closest points"""
        def rec_find_cells(parent_cell: Cell, main_vec: np.array) -> None:
            parent_vec = get_cell_vec(parent_cell, self.cell)

            """If cell in in the radius and cosine of the destination vector and candidate vector is bigger than vision angle
             and the cell is not obstacle, then cell is in the vision arc of the agent """
            if cell_in_radius(parent_vec) and cell_in_angle(parent_vec) and parent_cell.OBSTACLE == 0:

                cells.append((parent_cell, self.return_cell_affordance(parent_cell)))
                visited.add(parent_cell)

                for cell_child in parent_cell.neighborhood:
                    if cell_child not in visited:
                        rec_find_cells(cell_child, main_vec)
            else:
                return


        target_vector = get_cell_vec(self.target, self.cell)
        cells = []
        visited = set()
        for cell in self.cell.neighborhood:
            rec_find_cells(cell, target_vector)

        return cells



    def step(self):
        self.action()

    @staticmethod
    def calc_dest_dist(cell1:Cell, cell2: Cell) -> float:
        return np.linalg.norm(np.array(cell1.coordinate) - np.array(cell2.coordinate)).astype(float)


    def return_cell_affordance(self, cell: Cell) -> float:

        tile_val = self.tile_weight * ParkAgent.get_tile_value(cell)

        distance_diff = ParkAgent.calc_dest_dist(cell, self.cell) + ParkAgent.calc_dest_dist(self.target,
                                                                                             cell) - self.curr_distance()
        distance_val = distance_diff * self.distance_weight

        return max(tile_val - distance_val, 0)

    def curr_distance(self):
        return ParkAgent.calc_dest_dist(self.target, self.cell)


    """Each cell has only one type - other types values are equal to 0 - so adding 
    everything up we get the cell value, without checking the type"""
    @staticmethod
    def get_tile_value(cell: Cell) -> float:
        #return cell.SIDEWALK + cell.GRASS + cell.OBSTACLE
        if cell.SIDEWALK == Terrain.SIDEWALK.value:
            return 100.0
        elif cell.GRASS == Terrain.GRASS.value:
            return cell.GRASS_POPULARITY
        else: return 0.0
