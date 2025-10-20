import solara
from mesa.visualization import SpaceRenderer, SolaraViz
from model import ParkModel
from visualisation import visualise_agent


@solara.component
def page():
    model = ParkModel(10, 20, 20)
    model.setup()

    renderer = SpaceRenderer(model=model, backend="altair").render(
        agent_portrayal=visualise_agent
    )

    model_params = {
        "num_agents": {
            "type": "SliderInt",
            "value": 10,
            "label": "Number of agents",
            "min": 1,
            "max": 100,
            "step": 1,
        },
        "width": 20,
        "height": 20,
    }

    page_element = SolaraViz(
        model,
        renderer,
        model_params=model_params,
        name="Park simulation - test"
    )

    return page_element


Page = page
