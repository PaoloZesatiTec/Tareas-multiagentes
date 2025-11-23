from random_agents.agent import RandomAgent, ObstacleAgent, FloorAgent, StationAgent
from random_agents.model import RandomModel

from mesa.visualization import (
    Slider, SolaraViz, make_plot_component, make_space_component,
)
from mesa.visualization.components import AgentPortrayalStyle


def roomba_portrayal(agent):
    if agent is None:
        return

    portrayal = AgentPortrayalStyle(size=50, marker="o")

    if isinstance(agent, RandomAgent):
        portrayal.color = "green"
        portrayal.size = 80

    elif isinstance(agent, StationAgent):
        portrayal.color = "blue"
        portrayal.marker = "^"
        portrayal.size = 100

    elif isinstance(agent, ObstacleAgent):
        portrayal.color = "gray"
        portrayal.marker = "s"
        portrayal.size = 100

    elif isinstance(agent, FloorAgent):
        portrayal.color = "lightgray" if agent.fully_clean else "brown"
        portrayal.marker = "s"
        portrayal.size = 80
        portrayal.alpha = 0.6

    return portrayal


model_params = {
    "seed": {"type": "InputText", "value": 42, "label": "Random Seed"},
    "num_agents": Slider("Number of Roombas", 1, 1, 10),
    "width": Slider("Grid Width", 28, 10, 50),
    "height": Slider("Grid Height", 28, 10, 50),
    "num_obstacles": Slider("Number of Obstacles", 15, 0, 100),
    "num_dirty_tiles": Slider("Number of Dirty Tiles", 10, 10, 50),
    "max_steps": Slider("Maximum Steps", 800, 0, 1500),
}


def post_process_space(ax):
    ax.set_aspect("equal")


space_component = make_space_component(
    roomba_portrayal,
    draw_grid=False,
    post_process=post_process_space,
)


def post_process_tiles(ax):
    ax.set_ylabel("Percentage of Clean Tiles")
    ax.set_xlabel("Steps")
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))


tiles_plot = make_plot_component(
    {"Percentage Clean Tiles": "tab:Green"},
    post_process=post_process_tiles,
)


# movement tracking for up to 10 roombas
colors = [
    "tab:red", "tab:blue", "tab:purple", "tab:orange", "tab:cyan",
    "tab:pink", "tab:olive", "tab:gray", "navy", "gold"
]

roomba_movements_dict = {
    f"Roomba {i+1}": colors[i] for i in range(10)
}


def post_process_movements(ax):
    ax.set_ylabel("Number of Movements")
    ax.set_xlabel("Steps")
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5))


movements_plot = make_plot_component(
    roomba_movements_dict,
    post_process=post_process_movements,
)


model = RandomModel(
    num_agents=model_params["num_agents"].value,
    width=model_params["width"].value,
    height=model_params["height"].value,
    num_obstacles=model_params["num_obstacles"].value,
    num_dirty_tiles=model_params["num_dirty_tiles"].value,
    seed=model_params["seed"]["value"],
    max_steps=model_params["max_steps"].value,
)


page = SolaraViz(
    model,
    components=[space_component, tiles_plot, movements_plot],
    model_params=model_params,
    name="Roomba Cleaning Simulation",
)
