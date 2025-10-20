from mesa.visualization.components.portrayal_components import AgentPortrayalStyle
from cell import Cell
from agent import ParkAgent

def visualise_agent(agent):
    if isinstance(agent, Cell):
        color = "green" if agent.cell_type == 0 else "gray"
        size = 50
    elif isinstance(agent, ParkAgent):
        color = "blue"
        size = 50
    return AgentPortrayalStyle(color=color, size=size, zorder=1)