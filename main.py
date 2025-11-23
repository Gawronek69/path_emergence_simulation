from matplotlib.figure import Figure
from mesa.visualization import SolaraViz
from mesa.visualization.components.matplotlib_components import make_mpl_space_component

import solara
import seaborn as sns

from model import ParkModel
from visualisation import *

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("simulation_performance.log"),
        logging.StreamHandler()
    ]
)


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

model = ParkModel(5,100,100)
model.setup()

def post_process(ax):
    fig = ax.get_figure()
    fig.set_size_inches(10,10)


@solara.component
def HeatMap(model:ParkModel):
    print("HeatMap", type(model))
    fig = Figure(figsize=(20,14), dpi=150)
    ax = fig.subplots()

    sns.heatmap(
        data=np.flipud(model.heatmap),
        ax=ax,
        cmap="Oranges",
        vmin=0,
        vmax=model.heatmap.max(),
    )

    ax.set_title(f"Tiles visitation density for step {model.step_count}")

    return solara.FigureMatplotlib(fig)


space = make_mpl_space_component(
    agent_portrayal=agent_portrayal,
    propertylayer_portrayal=propertylayer_portrayal,
    draw_grid=True,
    post_process=post_process
)


page = SolaraViz(
    model,
    components=[space, (HeatMap, 1)],
    model_params=model_params,
    name="Test model"
)
