import mesa
from mesa.discrete_space import OrthogonalMooreGrid

from environment import TestEnvironment
from agent import ParkAgent
from utils import entrances

class ParkModel(mesa.Model):
    def __init__(self, num_agents=5, width=100, height=100, seed = 42):
        super().__init__(seed=seed)
        self.num_agents = num_agents
        self.grid = OrthogonalMooreGrid((width, height), torus=False, random=self.random)
        self.environment = TestEnvironment(width, height)
        self.step_count = 0
        self.spawn_cells = None

    def setup(self):
        terrain, obstacles = self.environment.create()
        self.grid.add_property_layer(terrain)
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
        )


    def step(self):
        self.step_count += 1
        if self.step_count % 10 == 0:
            self.spawn_agents(3)
        self.agents.shuffle_do("step")
