from mesa.visualization.components.portrayal_components import AgentPortrayalStyle

from agent import ParkAgent


def visualise_agent(agent):

    if isinstance(agent, ParkAgent):
        color = "blue"
        size = 10
        marker="o"
    else:
        color = "lightgreen" if agent.cell_type == 0 else "gray"
        size=100
        marker="s"
    x, y = agent.pos

    return AgentPortrayalStyle(
        color=color,
        size=size,
        alpha=1.0,
        marker=marker,
        edgecolors="black",
        x=x + 0.5,
        y=y + 0.5
    )