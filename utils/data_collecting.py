
def gather_steps(model) -> list[tuple[int, int]]:
    return [agent.pos for agent in model.agents]

