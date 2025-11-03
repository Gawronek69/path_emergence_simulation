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
    def __init__(self, num_agents=5, width=100, height=100, seed = 42, agent_params : dict = None):
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
            if cell.coordinate in entrances.doria_pamphil_west
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



    @classmethod
    def create_agents(cls, model, n, cell, target, **agent_kwargs):
        agents = []
        for i in range(n):
            a = cls(model, cell[i], target[i], **agent_kwargs)
            agents.append(a)
            model.agents.append(a)
            model.grid[cell[i]].add_agent(a)
        return agents

    def step(self):
        self.data_collector.collect(self)

        self.populate_heatmap()

        self.step_count += 1
        if self.step_count % 10 == 0 and len(self.agents) <= 15:
            self.spawn_agents(3)


        del_agents= [agent for agent in self.agents if agent.target == agent.cell]
        self.remove_agents(del_agents)
        self.agents.shuffle_do("step")
        for agent in self.agents:
            if agent.cell.GRASS == Terrain.GRASS.value:
                self.grid.GRASS_POPULARITY.data[agent.cell.coordinate] += 10




    def remove_agents(self, agents: list[CellAgent]) -> None:
        for agent in agents:
            self.agents.remove(agent)
            self.grid[agent.cell.coordinate].remove_agent(agent)

    def populate_heatmap(self):
        steps = self.data_collector.get_model_vars_dataframe()['Steps'].iloc[self.step_count]

        for (x, y) in steps:
            self.heatmap[x, y] += 1

