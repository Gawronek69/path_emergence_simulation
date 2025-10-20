import mesa
from mesa.agent import AgentSet
from mesa.space import MultiGrid

from environment import TestEnvironment
from agent import ParkAgent

class ParkModel(mesa.Model):
    def __init__(self, num_agents, width, height, seed = 42):
        super().__init__(seed=seed)
        self.num_agents = num_agents
        self.grid = MultiGrid(width, height, torus=False)
        self.environment = TestEnvironment(width, height)

    def setup(self):
        self.environment.create(self)
        self.create_agents()

    def create_agents(self):
        for i in range(self.num_agents):
            agent = ParkAgent(self, f"Agent_{i}")
            self.grid.place_agent(agent,self.random.choice(self.environment.sidewalk_coords))


    def step(self):
        self.agents.shuffle_do("step")
