import mesa
from mesa.discrete_space import OrthogonalMooreGrid

from environment import TestEnvironment
from agent import ParkAgent

class ParkModel(mesa.Model):
    def __init__(self, num_agents=5, width=100, height=100, seed = 42):
        super().__init__(seed=seed)
        self.num_agents = num_agents
        self.grid = OrthogonalMooreGrid((width, height), torus=False, random=self.random)
        self.environment = TestEnvironment(width, height)

    def setup(self):
        terrain, obstacles = self.environment.create()
        self.grid.add_property_layer(terrain)
        self.grid.add_property_layer(obstacles)
        self.create_agents()

    def create_agents(self):
        sidewalk_cells = [
            cell for cell in self.grid.all_cells.cells
            if getattr(cell, "sidewalk", False)
        ]

        ParkAgent.create_agents(
            model=self,
            n=self.num_agents,
            cell=self.random.sample(sidewalk_cells, k=self.num_agents),
        )


    def step(self):
        self.agents.shuffle_do("step")
