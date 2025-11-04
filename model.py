import math

import mesa
from mesa import DataCollector
from mesa.discrete_space import OrthogonalMooreGrid, CellAgent


from environment import TestEnvironment
from agent import ParkAgent
from utils.terrains import Terrain
from utils import entrances, data_collecting
from utils.data_collecting import gather_steps
import numpy as np


class ParkModel(mesa.Model):
    def __init__(self, num_agents=5, width=100, height=100, seed = 42, kind="normal", grass_decay_rate=0.2, grass_growth_probability=0.3, agent_params : dict = None):
        super().__init__(seed=seed)
        self.num_agents = num_agents
        self.grid = OrthogonalMooreGrid((width, height), torus=False, random=self.random)
        self.environment = TestEnvironment(width, height)
        self.step_count = 0
        self.spawn_cells = None
        self.data_collector = DataCollector(
            model_reporters={"Steps": gather_steps}
        )
        self.heatmap = np.zeros((width, height))
        self.agent_params = agent_params
        self.kind = kind
        self.grass_decay_rate = grass_decay_rate
        self.grass_growth_probability = grass_growth_probability

    def __str__(self):
        return f"Model with params: {self.agent_params} and seed {self._seed}"

    def setup(self):
        terrain, obstacles, grass, grass_popularity = self.environment.create()
        self.grid.add_property_layer(terrain)
        self.grid.add_property_layer(grass)
        self.grid.add_property_layer(obstacles)
        self.grid.add_property_layer(grass_popularity)


        self.spawn_cells = [
            cell
            for cell in self.grid.all_cells
            if cell.coordinate in entrances.hampstead
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

        self.populate_heatmap()

        self.step_count += 1
        if self.step_count % 10 == 0 and len(self.agents) <= 15:
            self.spawn_agents(3)


        del_agents= [agent for agent in self.agents if agent.target == agent.cell]
        self.remove_agents(del_agents)
        self.agents.shuffle_do("step")
        agent_cells = self._handle_grass_decay()
        self._handle_grass_growth(agent_cells)

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
        return agent_cells

    """Function that simulates grass regrowth"""
    def _handle_grass_growth(self, agent_cells):
        for cell in self.grid.all_cells:
            if cell.GRASS == Terrain.GRASS.value and cell not in agent_cells:
                value = self.grid.GRASS_POPULARITY.data[cell.coordinate]

                """Reducing only the medium paths"""
                if 40 < value < 80 and self.random.random() < self.grass_growth_probability:
                    self.grid.GRASS_POPULARITY.data[cell.coordinate] -= 1



    def remove_agents(self, agents: list[CellAgent]) -> None:
        for agent in agents:
            self.agents.remove(agent)
            self.grid[agent.cell.coordinate].remove_agent(agent)

    def populate_heatmap(self):
        steps = self.data_collector.get_model_vars_dataframe()['Steps'].iloc[self.step_count]

        for (x, y) in steps:
            self.heatmap[x, y] += 1

