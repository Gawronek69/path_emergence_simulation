import math

import mesa
from mesa import DataCollector
from mesa.discrete_space import OrthogonalMooreGrid, CellAgent
from mesa.experimental.cell_space import PropertyLayer
from scipy.ndimage import binary_dilation

from environment import TestEnvironment
from agent import ParkAgent
from utils.terrains import Terrain
from utils.images import binarize_desired_paths
from utils.data_collecting import gather_steps
import numpy as np


class ParkModel(mesa.Model):
    def __init__(self, num_agents=5, width=100, height=100, seed = 41, kind="normal", grass_decay_rate=0.8, grass_growth_probability=0.3, agent_params : dict = None, obstacle_margin_percentage=0.5):
        super().__init__(seed=seed)
        self.num_agents = num_agents
        self.grid = OrthogonalMooreGrid((width, height), torus=False, random=self.random)
        self.environment = TestEnvironment(width, height, "doria_pamphil")
        self.step_count = 0
        self.spawn_cells = None
        self.data_collector = DataCollector(
            model_reporters={"Steps": gather_steps}
        )
        self.heatmap = np.zeros((width, height))
        self.agent_params = agent_params
        self.kind = kind
        self.grass_decay_rate = grass_decay_rate
        self.obstacle_margin_percentage = obstacle_margin_percentage
        self.grass_growth_probability = grass_growth_probability
        self.agents_vision = PropertyLayer(
            "VISION", dimensions=(width, height), default_value=0, dtype=int
        )
        self.targets_vision = PropertyLayer(
            "SUBTARGETS", dimensions=(width, height), default_value=0, dtype=int
        )

    def __str__(self):
        return f"Model with params: {self.agent_params} and seed {self._seed}"

    def setup(self):
        terrain, obstacles, obstacles_margin, grass, grass_popularity = self.environment.create()
        self.grid.add_property_layer(terrain)
        self.grid.add_property_layer(grass)
        self.grid.add_property_layer(obstacles)
        self.grid.add_property_layer(obstacles_margin)
        self.grid.add_property_layer(grass_popularity)
        self.grid.add_property_layer(self.agents_vision)
        self.grid.add_property_layer(self.targets_vision)


        self.spawn_cells = [
            cell
            for cell in self.grid.all_cells
            if cell.coordinate in self.environment.entrances
        ]
        self.spawn_agents(3)




    def spawn_agents(self, num_agents):

        if self.agent_params is None:
            self.agent_params = {}

        ParkAgent.create_agents(
            model=self,
            n=num_agents,
            cell=self.random.sample(self.spawn_cells, k=num_agents),
            target = self.random.sample(self.spawn_cells, k=num_agents),
            **self.agent_params
        )

    def step(self):
        self.data_collector.collect(self)
        self.grid.VISION.data = self.grid.VISION.data * 0
        self.populate_heatmap()

        self.step_count += 1
        if self.step_count % 10 == 0 and len(self.agents) <= 15:
            self.spawn_agents(3)


        del_agents= [agent for agent in self.agents if agent.target == agent.cell]
        self.remove_agents(del_agents)
        self.agents.shuffle_do("step")
        agent_cells = self._handle_grass_decay()
        #self._handle_grass_growth(agent_cells)

        if self.step_count%100 == 0:
            print("Step: ", self.step_count, ",accuracy: ", self.calculate_accuracy()[0])

    """Function that simulates grass decay"""
    def _handle_grass_decay(self):
        agent_cells = []
        for agent in self.agents:
            agent_cells.append(agent.cell)
            if agent.cell.GRASS == Terrain.GRASS.value:
                value = self.grid.GRASS_POPULARITY.data[agent.cell.coordinate]
                increment = max(1, math.ceil(self.grass_decay_rate * value))
                if value + increment > 100:
                    self.grid.GRASS_POPULARITY.data[agent.cell.coordinate] = 100
                else:
                    self.grid.GRASS_POPULARITY.data[agent.cell.coordinate] += math.ceil(increment)
            if agent.cell.OBSTACLE_MARGIN == Terrain.OBSTACLE_MARGIN.value:
                value = self.obstacle_margin_percentage * self.grid.GRASS_POPULARITY.data[agent.cell.coordinate]
                increment = max(1, math.ceil(self.grass_decay_rate * value * self.obstacle_margin_percentage))
                if value + increment > 40:
                    self.grid.GRASS_POPULARITY.data[agent.cell.coordinate] = 40
                else:
                    self.grid.GRASS_POPULARITY.data[agent.cell.coordinate] += math.ceil(increment)
        return agent_cells

    """Function that simulates grass regrowth"""
    def _handle_grass_growth(self, agent_cells):
        for cell in self.grid.all_cells:
            if cell.GRASS == Terrain.GRASS.value and cell not in agent_cells:
                value = self.grid.GRASS_POPULARITY.data[cell.coordinate]

                """Reducing only the medium paths"""
                if 40 < value < 80 and self.random.random() < self.grass_growth_probability:
                    self.grid.GRASS_POPULARITY.data[cell.coordinate] -= 1
            if cell.OBSTACLE_MARGIN == Terrain.OBSTACLE_MARGIN.value and cell not in agent_cells:
                self.grid.GRASS_POPULARITY.data[cell.coordinate] *= self.obstacle_margin_percentage

    def remove_agents(self, agents: list[ParkAgent]) -> None:
        for agent in agents:

            if agent.subtarget:
                self.grid.SUBTARGETS.data[agent.subtarget.coordinate] -= 1

            self.agents.remove(agent)
            self.grid[agent.cell.coordinate].remove_agent(agent)

    def populate_heatmap(self):
        steps = self.data_collector.get_model_vars_dataframe()['Steps'].iloc[self.step_count]

        for (x, y) in steps:
            self.heatmap[x, y] += 1

    def calculate_accuracy(self, include_dilatation=False):
        terrain_after_simulation = self.grid.GRASS_POPULARITY.data
        #we hate to determine the threshold
        created_paths = (terrain_after_simulation > 10).astype(int)
        created_paths = np.rot90(created_paths, k=1)
        if include_dilatation:  created_paths = binary_dilation(created_paths, iterations=1).astype(int)
        reference_paths = np.load(f"utils/desired_paths_matrixes/" + self.environment.park_name + ".npy")
        mask = reference_paths==1
        accuracy = np.sum(created_paths[mask] == 1) / np.sum(mask)
        return accuracy, created_paths, reference_paths


