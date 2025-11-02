
def gather_steps(model) -> list[tuple[int, int]]:
    return [agent.cell.coordinate for agent in model.agents]

