import mesa

class HelloAgent(mesa.Agent):
    def __init__(self, model):
        super().__init__(model)


        #TODO load starting point from random set of starting points in env
        self.x = 0
        self.y = 0

    def action(self):
        pass


