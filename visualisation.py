from matplotlib.colors import ListedColormap
from mesa.experimental.cell_space import PropertyLayer
from mesa.visualization.components.portrayal_components import AgentPortrayalStyle, PropertyLayerStyle

from utils.terrains import Terrain
import numpy as np

def propertylayer_portrayal(layer: PropertyLayer) -> PropertyLayerStyle|None:

    """
    How to create good visualisation
    We use alpha to change the visibility of the cells - currently it tries to
    paint each cell with specific color so the last property layer loaded in grid
    just covers the entire map in it's color - so we use the fact that the points
    that have meaning in the property value have specific value attached to it,
    so we use a copy of layer data and set it to true/false array, and change it's type to float
    so the meaningful cells have visibility == 1 and the useles ones have opacity set to 0
    """

    if layer.name == "OBSTACLE":
        print(type(layer))
        cmap = ListedColormap(["black"])
        return PropertyLayerStyle(
            colormap=cmap,
            alpha=(np.transpose(layer.data) == Terrain.OBSTACLE.value).astype(float), # I hate the people who thought of having
            # to transpose alpha to match the grid actual values
            colorbar=False,

        )
    elif layer.name == "GRASS_POPULARITY":
        return PropertyLayerStyle(
            colormap="summer",
            alpha= (np.transpose(layer.data) >= Terrain.GRASS.value).astype(float),
            colorbar=True,
            vmin= Terrain.GRASS.value,
            #I had to use it to somehow combine popularity layer with grass (to avoid drawing grass on sidewalks)
            vmax=100,
        )
    elif layer.name == "SIDEWALK":
        return PropertyLayerStyle(
            colormap=ListedColormap(["gray"]),
            alpha= (np.transpose(layer.data) == Terrain.SIDEWALK.value).astype(float),
            colorbar=False
        )


def agent_portrayal(agent):
    return {
        "marker": "o",
        "color": "red",
        "size": 500
    }