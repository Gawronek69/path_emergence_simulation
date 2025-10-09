import mesa

from agent import HelloAgent


class HelloModel(mesa.Model):
    def __init__(self, n, seed = 42):
        super().__init__(seed=seed)
        self.num_agents = n
        HelloAgent.create_agents(model=self, n = self.num_agents)

    def step(self):
        self.agents.shuffle_do("say_hello")