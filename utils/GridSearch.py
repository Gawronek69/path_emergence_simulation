import os
import multiprocessing as mp
from model import ParkModel
import random
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

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

    def plot_heatmaps(self) -> None:

        if not os.path.isdir(self.directory):
            os.mkdir(self.directory)

        heat_path = os.path.join(self.directory, "heatmaps")
        if not os.path.exists(heat_path):
            os.mkdir(heat_path)


        for i, model in enumerate(self.models_data):

            plt.figure(figsize=(20, 14), dpi=300)

            model_heatmap_data = model["heatmap"]
            model_params = model["params"]

            sns.heatmap(
                data=np.flipud(model_heatmap_data),
                cmap="Oranges",
                vmin=0,
                vmax=model_heatmap_data.max(),
            )

            print(f"Saving to {self.directory}/heatmaps/{model_params}{i}.png")
            plt.title(f"{model_params}")
            plt.savefig(f"{self.directory}/heatmaps/{model_params}{i}.png")
            plt.close()

    def get_acc(self) -> float:
        pass

    def plot_map_and_heat(self) -> None:
        pass

    def plot_map_state(self, agents: bool = True) -> None:

        if not os.path.isdir(self.directory):
            os.mkdir(self.directory)

        map_path = os.path.join(self.directory, "maps")
        if not os.path.exists(map_path):
            os.mkdir(os.path.join(self.directory, "maps"))

        def get_cell_color(val: int):
            if val >= 100:
                return "grey"
            elif val == 0:
                return "black"
            else:
                cmap = plt.get_cmap("summer")
                norm = plt.Normalize(vmin=1, vmax=100)
                print(cmap(norm(val)))
                return cmap(norm(val))

        for index, model in enumerate(self.models_data):
            model_name = model["params"]
            model_map_data = model["cells"]
            model_agents_pos = model["agents"]

            plt.figure(figsize=(20, 14), dpi=300)
            ax = plt.gca()
            y, x = model_map_data.shape
            ax.set_xlim(0, x)
            ax.set_ylim(0, y)
            ax.set_aspect("equal")

            for j in range(y):
                for i in range(x):
                    color = get_cell_color(model_map_data[j, i])
                    ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=color, edgecolor=None))

            if agents:
                for (j, i) in model_agents_pos:
                    ax.add_patch(plt.Circle((j, i), 1, facecolor="red", edgecolor=None))

            print(f"Saving to {self.directory}/maps/{model_name}{index}.png")
            plt.title(f"{model_name}")
            plt.savefig(f"{self.directory}/maps/{model_name}{index}.png")
            plt.close()


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
            models_data.append({"params" : model_item, "heatmap": model.heatmap, "cells": get_map_matrix(), "agents": [agent.cell.coordinate for agent in model.agents]})

        queue.put(models_data)

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