from mesa import Agent
from mesa.discrete_space import Cell
'''
Class representing static agent - Cell, that can be placed on mesa.space.Multigrid 
and hold information about specific cell.
'''
class Cell(Agent):
    def __init__(self, unique_id, model, cell_type):
        super().__init__(model)
        self.unique_id = unique_id
        self.cell_type = cell_type