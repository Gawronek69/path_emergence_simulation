import mesa
from mesa.discrete_space import CellAgent

class ParkAgent(CellAgent):
    def __init__(self, model, cell):
        super().__init__(model)
        self.cell = cell

    def action(self):
        possible_cells = [c for c in self.cell.neighborhood if c.is_empty and c.sidewalk==True]

        if len(possible_cells) > 0:
            self.cell = self.model.random.choice(possible_cells)

    def step(self):
        self.action()


