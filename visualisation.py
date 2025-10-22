from matplotlib.colors import ListedColormap
from mesa.visualization.components.portrayal_components import AgentPortrayalStyle, PropertyLayerStyle

def propertylayer_portrayal(layer):
    if layer.name == "sidewalk":
        cmap = ListedColormap(["green", "gray"])
        return PropertyLayerStyle(
            colormap=cmap,
            alpha=1,
            colorbar=False,
            vmin=0,
            vmax=1,
        )
    elif layer.name == "obstacles":
        cmap = ListedColormap(["black"])
        return PropertyLayerStyle(
            colormap=cmap,
            alpha=layer.data.astype(float),
            colorbar=False,
            vmin=0,
            vmax=1,
        )

def agent_portrayal(agent):
    return {
        "marker": ">",
        "color": "blue",
        "size": 40
    }