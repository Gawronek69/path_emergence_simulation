from typing import Any

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
        self.distance_weight = distance_weight # distance_weight value should never be equal to 0
        # else it will not reach the destination in some scenarios
        # cuz it will wiggle around the destination


    def action(self):
        """If agent reached the subtarget then we have to find next subtarget"""
        if self.subtarget and self.subtarget.coordinate == self.cell.coordinate:
            self.subtarget = None

        """Find which point in the vision arc is best for next destination of the agent"""
        if self.subtarget is None:
            candidates = self.select_subtarget()

            best_cell = None
            best_aff = 0
            for candidate, candidate_aff in candidates:
                # print(candidate, candidate_aff, "CELL TYPE", self.get_tile_value(candidate), "CELL DISTANCE", self.calc_dest_dist(self.cell, candidate) + self.calc_dest_dist(self.target, candidate))
                if candidate_aff > best_aff:
                    best_aff = candidate_aff
                    best_cell = candidate
            self.subtarget = best_cell
            # print("CHOSEN CELL", self.subtarget)

        cell_dist = self.target

        # print("TARGET", self.target)
        # print("CURRENT CELL", self.cell)

        if self.subtarget:
            cell_dist = self.subtarget

        possible_cells = [(c, self.calc_dest_dist(cell_dist, c)) for c in self.cell.neighborhood if c.is_empty and (c.SIDEWALK == Terrain.SIDEWALK.value or c.GRASS == Terrain.GRASS.value)]

        max_dist = self.curr_distance()
        cell_to_chose = None

        for cell, distance in possible_cells:
            if distance < max_dist:
                cell_to_chose = cell
                max_dist = distance

        if cell_to_chose:
            self.cell = cell_to_chose

        # if len(possible_cells) > 0:
        #     self.cell = self.model.random.choice(possible_cells)

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

        tile_val = self.tile_weight * (ParkAgent.get_tile_value(cell) - 1)

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
        return cell.SIDEWALK + cell.GRASS + cell.OBSTACLE