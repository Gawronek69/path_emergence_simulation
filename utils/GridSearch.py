import os
import multiprocessing as mp

from model import ParkModel
import random
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from utils.terrains import Terrain

"""GridSearch like class for generating many simulataions with different params at once
use run_models to run the simulations and plot_heatmaps to create the results"""
class GridSearch:

    def __init__(self, directory:str = os.getcwd(), samples:int = 5,   n_workers : int = 1, stop_step:int = 100, **kwargs):
        self.directory = directory
        self.samples = samples
        self.n_workers = n_workers
        self.stop_step = stop_step
        self.model_params = kwargs
        self.params = self.initialize()
        self.models_data = []


    def initialize(self) -> list[dict]:
        params = []
        for i in range(self.samples):
            agent_params = dict()
            for name, param in self.model_params.items():

                if isinstance(param, list):
                    agent_params[name] = random.choice(param)
                else:
                    agent_params[name] = param

            params.append(agent_params)

        return params


    """plots heatmaps of agents movements from created simulations"""
    def plot_heatmaps(self) -> None:

        plot_dirname = "heatmaps"

        self.check_create_dir(plot_dirname)


        for i, model in enumerate(self.models_data):

            plt.figure(figsize=(20, 14), dpi=300)
            ax = plt.gca()
            model_params = model["params"]

            self.get_heatmap(ax, model_idx= i)

            print(f"Saving to {self.directory}/{plot_dirname}/{model_params}{i}.png")
            plt.title(f"{model_params}")
            plt.savefig(f"{self.directory}/{plot_dirname}/{model_params}{i}.png")
            plt.close()

    """function for getting the score of the simulation compared to the real emerged paths"""
    def get_acc(self) -> float:
        for model in self.models_data:
            print("Accuracy of ", model["params"], " : ", model["accuracy"])

    """plots maps states and heatmaps of agents movement together from created simulations"""
    def plot_map_and_heat(self, agents: bool = True) -> None:

        plot_dirname = "combined"

        self.check_create_dir(plot_dirname)

        for index, model in enumerate(self.models_data):
            model_name = model["params"]
            model_map_data = model["cells"]

            plt.figure(figsize=(20, 14), dpi=300)
            ax = plt.gca()
            y, x = model_map_data.shape
            ax.set_xlim(0, x)
            ax.set_ylim(0, y)
            ax.set_aspect("equal")


            self.get_map_state(ax, model_idx=index, plot_agents=agents, alpha=1)
            self.get_heatmap(ax, model_idx=index, alpha=0.3)

            print(f"Saving to {self.directory}/{plot_dirname}/{model_name}{index}.png")
            plt.title(f"{model_name}")
            plt.savefig(f"{self.directory}/{plot_dirname}/{model_name}{index}.png")
            plt.close()

    """plots maps state from created simulations"""
    def plot_map_state(self, agents: bool = True) -> None:

        plot_dirname = "maps"

        self.check_create_dir(plot_dirname)

        for index, model in enumerate(self.models_data):
            model_name = model["params"]
            model_map_data = model["cells"]

            plt.figure(figsize=(20, 14), dpi=300)
            ax = plt.gca()
            y, x = model_map_data.shape
            ax.set_xlim(0, x)
            ax.set_ylim(0, y)
            ax.set_aspect("equal")

            self.get_map_state(ax, model_idx= index, plot_agents=agents, alpha=1)

            print(f"Saving to {self.directory}/{plot_dirname}/{model_name}{index}.png")
            plt.title(f"{model_name}")
            plt.savefig(f"{self.directory}/{plot_dirname}/{model_name}{index}.png")
            plt.close()

    """creates heatmap plot"""
    def get_heatmap(self, ax: plt.Axes, model_idx: int,  alpha: float = 1, ) -> None:

        heatmap_data = self.models_data[model_idx]["heatmap"]

        sns.heatmap(
            data=np.transpose(heatmap_data),
            cmap="Oranges",
            ax = ax,
            vmin=0,
            vmax=heatmap_data.max(),
            alpha=alpha,
        )

        ax.invert_yaxis()

    """creates map state plot"""
    def get_map_state(self, ax: plt.Axes, model_idx: int, alpha: float = 1, plot_agents: bool = True) -> None:

        def get_cell_color(val: int):
            if val >= Terrain.SIDEWALK.value:
                return "grey"
            elif val == 0:
                return "black"
            else:
                cmap = plt.get_cmap("summer")
                norm = plt.Normalize(vmin=1, vmax=100)
                return cmap(norm(val))

        model_map_data = self.models_data[model_idx]["cells"]
        model_agents_pos = self.models_data[model_idx]["agents"]

        y, x = model_map_data.shape

        for j in range(y):
            for i in range(x):
                color = get_cell_color(model_map_data[j, i])
                ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=color, edgecolor=None, alpha=alpha))

        if plot_agents:
            for (j, i) in model_agents_pos:
                ax.add_patch(plt.Circle((j, i), 1, facecolor="red", edgecolor=None, alpha=alpha))



    """task for each process - creates models, runs the simulations and returns the simulation data to the queue"""
    def _model_task(self, model_params: list[dict], queue: mp.Queue) -> None:

        def get_coord_value(i: int, j: int) -> dict:
            grid = model.grid
            return grid.GRASS_POPULARITY.data[i,j] + grid.SIDEWALK.data[i,j]

        def get_map_matrix() -> np.array:
            map_data = np.zeros((model.grid.height, model.grid.width))
            for j in range(model.grid.height):
                for i in range(model.grid.width):
                    map_data[j, i] = get_coord_value(j,i)
            return map_data

        models_data = []
        for model_item in model_params:
            model = ParkModel(agent_params=model_item)
            model.setup()
            for _ in range(self.stop_step):
                model.step()
            models_data.append({"params" : model_item, "heatmap": model.heatmap, "cells": get_map_matrix(), "agents": [agent.cell.coordinate for agent in model.agents], "accuracy" : model.calculate_accuracy()})

        queue.put(models_data)

    """creates processes for running simulations and runs the tasks there"""
    def run_models(self):

        """Multiprocessing stuff so it will return models (cuz u cant pass as ref)"""
        manager = mp.Manager()
        results_queue = manager.Queue()
        chunk_size = (self.samples + self.n_workers - 1) // self.n_workers
        processes = []

        for i in range(self.n_workers):

            start_index: int = i * chunk_size
            end_index: int = start_index + chunk_size

            process = mp.Process(target=self._model_task, args=(self.params[start_index: end_index], results_queue))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()


        final_models = []

        while not results_queue.empty():
            final_models.extend(results_queue.get())

        self.models_data = final_models


    """Checks whether exists the directory for plot directories and the plot directories as well"""
    def check_create_dir(self, plot_dirname: str) -> None:

        if not os.path.isdir(self.directory):
            os.mkdir(self.directory)

        map_path = os.path.join(self.directory, plot_dirname)
        if not os.path.exists(map_path):
            os.mkdir(os.path.join(self.directory, plot_dirname))