from __future__ import annotations

from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from mesa.discrete_space import Cell
from utils.terrains import Terrain
from agent import  ParkAgent


class AbstractMetric(ABC):
    @abstractmethod
    def get_cells_rank(self, agent: ParkAgent) -> list[tuple[Cell, float]]:
        pass

    def __str__(self):
        return "abstract"

class ClosestMetric(AbstractMetric):

    def get_cells_rank(self, agent: ParkAgent) -> list[tuple[Cell, float]]:
        cell_dist = agent.target

        if agent.subtarget:
            cell_dist = agent.subtarget

        possible_cells = [(c, agent.calc_dest_dist(cell_dist, c)) for c in agent.cell.neighborhood if
                          (c.SIDEWALK == Terrain.SIDEWALK.value or c.GRASS == Terrain.GRASS.value)]

        possible_cells = sorted(possible_cells, key=lambda c: c[1])
        return possible_cells

    def __str__(self):
        return "normal"

class AffordanceMetric(AbstractMetric):

    def get_cells_rank(self, agent: ParkAgent) -> list[tuple[Cell, float]]:

        cell_dist = agent.target

        if agent.subtarget:
            cell_dist = agent.subtarget

        if cell_dist in agent.cell.neighborhood:
            return [(cell_dist, -1)]

        min_dist = ParkAgent.calc_dest_dist(cell_dist, agent.cell)

        possible_cells = [(c, agent.return_cell_affordance(c)) for c in agent.cell.neighborhood if
                          (c.SIDEWALK == Terrain.SIDEWALK.value or c.GRASS == Terrain.GRASS.value) and min_dist >= ParkAgent.calc_dest_dist(cell_dist, c)]

        possible_cells = sorted(possible_cells, key=lambda c: c[1], reverse=True)

        if len(possible_cells) == 0:
            possible_cells = [(c, agent.calc_dest_dist(cell_dist, c)) for c in agent.cell.neighborhood if
                          (c.SIDEWALK == Terrain.SIDEWALK.value or c.GRASS == Terrain.GRASS.value)]
            possible_cells = sorted(possible_cells, key=lambda c: c[1])

        return possible_cells

    def __str__(self):
        return "affordance"
