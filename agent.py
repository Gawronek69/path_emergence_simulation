import mesa

class ParkAgent(mesa.Agent):
    def __init__(self, model, unique_id):
        super().__init__(model)
        self.unique_id = unique_id

    def action(self):
        print(self.pos)
        neighbors = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        valid_steps = []
        for pos in neighbors:
            cell = self.model.grid.get_cell_list_contents([pos])[0]
            if cell.cell_type == 1:
                valid_steps.append(pos)
        if valid_steps:
            new_pos = self.random.choice(valid_steps)
            self.model.grid.move_agent(self, new_pos)

    def step(self):
        self.action()


