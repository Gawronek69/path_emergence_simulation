import solara
from mesa.visualization import SpaceRenderer, SolaraViz
from model import ParkModel
from visualisation import visualise_agent

@solara.component
def page():
    model = ParkModel(3, 20, 20)
    model.setup()

    renderer = SpaceRenderer(model=model, backend="matplotlib").render(
        agent_portrayal=visualise_agent
    )

    model_params = {
        "width": 20,
        "height": 15,
        "num_agents": {
            "type": "SliderInt",
            "value": 50,
            "label": "Number of agents:",
            "min": 10,
            "max": 100,
            "step": 1,
        }
    }

    page_element = SolaraViz(
        model,
        renderer,
        model_params=model_params,
        name="Test model"
    )

    return page_element

Page = page
