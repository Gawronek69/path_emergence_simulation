from mesa.visualization import SolaraViz
from mesa.visualization.components.matplotlib_components import make_mpl_space_component

from model import ParkModel
from visualisation import *


model_params = {
    "seed": {
        "type": "InputText",
        "value": 42,
        "label": "Seed",
    },
    "num_agents": {
        "type": "SliderInt",
        "value": 100,
        "label": "No. of Agents",
        "min": 10,
        "max": 1000,
        "step": 1,
    },
    "width": {
        "type": "SliderInt",
        "value": 100,
        "label": "Width",
        "min": 10,
        "max": 500,
        "step": 1,
    },
    "height": {
        "type": "SliderInt",
        "value": 100,
        "label": "Height",
        "min": 10,
        "max": 500,
        "step": 1,
    },
}

model = ParkModel(3,30,30)
model.setup()

def post_process(ax):
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

space = make_mpl_space_component(
    agent_portrayal=agent_portrayal,
    propertylayer_portrayal=propertylayer_portrayal,
    post_process=post_process,
    draw_grid=True,
)

page = SolaraViz(
    model,
    components=[space],
    model_params=model_params,
    name="Test model",
)
