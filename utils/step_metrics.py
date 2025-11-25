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

        if len(possible_cells) == 0:
            return [(cell_dist, -1)]

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

        if len(possible_cells) == 0:
            return [(cell_dist, -1)]

        return possible_cells

    def __str__(self):
        return "affordance"

class RandomBalancedMetric(AbstractMetric):
    def get_cells_rank(self, agent: ParkAgent) -> list[tuple[Cell, float]]:
        cell_dist = agent.target
        if agent.subtarget:
            cell_dist = agent.subtarget

        min_dist = ParkAgent.calc_dest_dist(cell_dist, agent.cell)

        possible_cells_dist = [(c, agent.calc_dest_dist(cell_dist, c)) for c in agent.cell.neighborhood if
                          (c.SIDEWALK == Terrain.SIDEWALK.value or c.GRASS == Terrain.GRASS.value)
                               and min_dist >= ParkAgent.calc_dest_dist(cell_dist, c)]


        possible_cells_aff = [(c, agent.return_cell_affordance(c)) for c in agent.cell.neighborhood if
                          (c.SIDEWALK == Terrain.SIDEWALK.value or c.GRASS == Terrain.GRASS.value)
                               and min_dist >= ParkAgent.calc_dest_dist(cell_dist, c)]

        possible_cells_dist = sorted(possible_cells_dist, key=lambda c: c[1])
        possible_cells_aff = sorted(possible_cells_aff, key=lambda c: c[1], reverse=True)

        ranks = {}

        for rank, (cell, value) in enumerate(possible_cells_dist):
            ranks[cell] = rank

        for rank, (cell, value) in enumerate(possible_cells_aff):
            ranks[cell] += rank

        ranks = [(cell, rank) for cell, rank in ranks.items()]
        ranks = sorted(ranks, key=lambda c: c[1])

        if len(ranks) == 0:
            return [(cell_dist, -1)]

        return ranks

    def __str__(self):
        return "balanced_random"


class MixedMetric(AbstractMetric):
    def get_cells_rank(self, agent: ParkAgent) -> list[tuple[Cell, float]]:
        cell_dist = agent.target

        if agent.subtarget:
            cell_dist = agent.subtarget

        possible_cells= [(c, agent.calc_dest_dist(cell_dist, c), agent.get_tile_value(c)) for c in agent.cell.neighborhood if
                          (c.SIDEWALK == Terrain.SIDEWALK.value or c.GRASS == Terrain.GRASS.value) and
                         c.OBSTACLE_MARGIN != Terrain.OBSTACLE_MARGIN.value and c not in agent.previous_cells]

        #if there is no possible steps for our agent - send him to the target and forget about him
        if len(possible_cells) == 0:
            return [(cell_dist, -1)]

        #for scaling values to the range 0-1
        min_dist = min(possible_cells, key=lambda x: x[1])
        max_dist = max(possible_cells, key=lambda x: x[1])
        min_aff = min(possible_cells, key=lambda x: x[2])
        max_aff = max(possible_cells, key=lambda x: x[2])
        d_dist = max_dist[1] - min_dist[1]
        d_aff = max_aff[2] - min_aff[2]

        def calculate_combination(c : tuple[Cell, float, float]) -> float:
            if d_aff == 0:
                return (c[1] - min_dist[1]) / d_dist #all have the same affordance
            else:
                dist_scaled = (c[1] - min_dist[1]) / d_dist
                aff_scaled = (c[2] - min_aff[2]) / d_aff
                return dist_scaled/aff_scaled

        candidates = [(c[0], calculate_combination(c)) for c in possible_cells]
        candidates = sorted(candidates, key=lambda c: c[1])
        return candidates

    def __str__(self):
        return "mixed"



