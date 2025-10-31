import mesa
from mesa import DataCollector
from mesa.discrete_space import OrthogonalMooreGrid, CellAgent


from environment import TestEnvironment
from agent import ParkAgent
from utils import entrances, data_collecting
from utils.data_collecting import gather_steps
import numpy as np


class ParkModel(mesa.Model):
    def __init__(self, num_agents=5, width=100, height=100, seed = 42):
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


    def setup(self):
        terrain, obstacles, grass = self.environment.create()
        self.grid.add_property_layer(terrain)
        self.grid.add_property_layer(grass)
        self.grid.add_property_layer(obstacles)


        self.spawn_cells = [
            cell
            for cell in self.grid.all_cells
            if cell.coordinate in entrances.doria_pamphil
        ]
        self.spawn_agents(3)


    def spawn_agents(self, num_agents):
        ParkAgent.create_agents(
            model=self,
            n=num_agents,
            cell=self.random.sample(self.spawn_cells, k=num_agents),
            target = self.random.sample(self.spawn_cells, k=num_agents)
        )


    def step(self):
        self.data_collector.collect(self)

        self.populate_heatmap()

        self.step_count += 1
        if self.step_count % 7 == 0:
            self.spawn_agents(4)

        del_agents= [agent for agent in self.agents if agent.target == agent.cell]
        self.remove_agents(del_agents)

        self.agents.shuffle_do("step")

    def remove_agents(self, agents: list[CellAgent]) -> None:
        for agent in agents:
            self.agents.remove(agent)
            self.grid[agent.cell.coordinate].remove_agent(agent)

    def populate_heatmap(self):
        steps = self.data_collector.get_model_vars_dataframe()['Steps'].iloc[self.step_count]

        for (x, y) in steps:
            self.heatmap[x, y] += 1

