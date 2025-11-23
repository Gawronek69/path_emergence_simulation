import os
import multiprocessing as mp

from model import ParkModel
import random
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from utils.step_metrics import AbstractMetric, ClosestMetric, AffordanceMetric
from utils.terrains import Terrain

"""GridSearch like class for generating many simulations with different params at once
use run_models to run the simulations and plot_heatmaps to create the results"""
class GridSearch:

    """ !!! Metric can be "normal" or "affordance" !!! """
    def __init__(self, directory:str = os.getcwd(), parks: str|list[str] = "doria_pamphil", seeds: int|list[int] = 42 , metric: str | list[str] = "normal" ,samples:int = 5,   n_workers : int = 1, stop_step:int = 100, **kwargs):
        self.directory = directory
        self.seeds = seeds
        self.samples = samples
        self.n_workers = n_workers
        self.stop_step = stop_step
        self.model_params = kwargs
        self.metric = metric
        self.parks = parks
        self.params = self.initialize()
        self.models_data = []


    def initialize(self) -> list[tuple[dict, int]]:
        params = []
        for i in range(self.samples):
            agent_params = dict()
            for name, param in self.model_params.items():

                if isinstance(param, list):
                    agent_params[name] = random.choice(param)
                else:
                    agent_params[name] = param

            if isinstance(self.seeds, list):
                model_seed = random.choice(self.seeds)
            else:
                model_seed = self.seeds

            if isinstance(self.metric, list):
                model_metric = random.choice(self.metric)
            else:
                model_metric = self.metric

            if isinstance(self.parks, list):
                model_park = random.choice(self.parks)
            else:
                model_park = self.parks

            params.append((agent_params, model_seed, model_metric, model_park))

        return params


    """plots heatmaps of agents movements from created simulations"""
    @staticmethod
    def _create_heatmaps(directory: str, models_data: list[dict]) -> None:

        plot_dirname = "heatmaps"

        GridSearch.check_create_dir(directory, plot_dirname)


        for index, model in enumerate(models_data):

            plt.figure(figsize=(20, 14), dpi=300)
            ax = plt.gca()
            model_name = model["params"]

            GridSearch.get_heatmap(ax, model)

            print(f"Saving to {directory}/{plot_dirname}/{model_name}{index}.png")
            plt.title(f"{model_name}")
            plt.savefig(f"{directory}/{plot_dirname}/{model_name}{index}.png")
            plt.close()

    """function for getting the score of the simulation compared to the real emerged paths"""
    @staticmethod
    def _create_acc(directory: str, models_data: list[dict]):
        plot_dirname = "accuracy"
        GridSearch.check_create_dir(directory, plot_dirname)

        for idx, model in enumerate(models_data):
            acc = model["accuracy"][0]
            created_paths = model["accuracy"][1]
            original_paths = model["accuracy"][2]

            f, ax = plt.subplots()
            ax.imshow(np.ma.masked_where(created_paths == 0, created_paths),cmap="Reds", alpha=0.7, vmin=0, vmax=1)
            ax.imshow(np.ma.masked_where(original_paths == 0, original_paths), cmap="Blues", alpha=0.7, vmin=0, vmax=1)
            ax.set_title(f"Accuracy: {acc}")

            save_path = os.path.join(directory, plot_dirname, f"{model['params']}{idx}.jpg")
            plt.savefig(save_path)
            plt.close(f)

            print("Accuracy of", model["params"], ":", model["accuracy"][0])

    """plots maps states and heatmaps of agents movement together from created simulations"""
    @staticmethod
    def _create_map_and_heat(directory:str,models_data: list[dict], agents: bool = True) -> None:

        plot_dirname = "combined"

        GridSearch.check_create_dir(directory, plot_dirname)

        for index, model in enumerate(models_data):

            model_name = model["params"]
            model_map_data = model["cells"]

            plt.figure(figsize=(20, 14), dpi=300)
            ax = plt.gca()
            y, x = model_map_data.shape
            ax.set_xlim(0, x)
            ax.set_ylim(0, y)
            ax.set_aspect("equal")


            GridSearch.get_map_state(ax, model, plot_agents=agents, alpha=1)
            GridSearch.get_heatmap(ax, model, alpha=0.3)

            print(f"Saving to {directory}/{plot_dirname}/{model_name}{index}.png")
            plt.title(f"{model_name}")
            plt.savefig(f"{directory}/{plot_dirname}/{model_name}{index}.png")
            plt.close()

    """plots maps state from created simulations"""
    @staticmethod
    def _create_map_state(directory:str,models_data: list[dict], agents: bool = True) -> None:

        plot_dirname = "maps"

        GridSearch.check_create_dir(directory, plot_dirname)

        for index, model in enumerate(models_data):

            model_name = model["params"]
            model_map_data = model["cells"]

            plt.figure(figsize=(20, 14), dpi=300)
            ax = plt.gca()
            y, x = model_map_data.shape
            ax.set_xlim(0, x)
            ax.set_ylim(0, y)
            ax.set_aspect("equal")

            GridSearch.get_map_state(ax, model, plot_agents=agents, alpha=1)

            print(f"Saving to {directory}/{plot_dirname}/{model_name}{index}.png")
            plt.title(f"{model_name}")
            plt.savefig(f"{directory}/{plot_dirname}/{model_name}{index}.png")
            plt.close()

    @staticmethod
    def _plot_task(function_name:str, models_data: list[dict], directory: str, func_params: dict) -> None:

        target_func = getattr(GridSearch, function_name)

        target_func(directory, models_data, **func_params)


    def _plot_functions(self, function_name:str, **kwargs) -> None:

        chunk_size = (len(self.models_data) + self.n_workers - 1) // self.n_workers
        processes = []

        for i in range(self.n_workers):
            start_index: int = i * chunk_size
            end_index: int = start_index + chunk_size
            processes.append((function_name, self.models_data[start_index: end_index], self.directory, kwargs))

        with mp.Pool(processes=self.n_workers) as pool:
            pool.starmap(GridSearch._plot_task, processes)


    def plot_heatmaps(self) -> None:
        self._plot_functions("_create_heatmaps")

    def plot_maps(self, agents: bool = True) -> None:
        self._plot_functions("_create_map_state", agents=agents)

    def plot_maps_heats(self, agents: bool = True) -> None:
        self._plot_functions("_create_map_and_heat", agents=agents)

    def get_acc(self) -> None:
        self._plot_functions("_create_acc")

    """creates heatmap plot"""
    @staticmethod
    def get_heatmap(ax: plt.Axes, models_data: dict, alpha: float = 1, ) -> None:

        heatmap_data = models_data["heatmap"]

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
    @staticmethod
    def get_map_state(ax: plt.Axes, models_data: dict, alpha: float = 1, plot_agents: bool = True) -> None:

        def get_cell_color(val: int):
            if val >= Terrain.SIDEWALK.value:
                return "grey"
            elif val == 0:
                return "black"
            else:
                cmap = plt.get_cmap("summer")
                norm = plt.Normalize(vmin=1, vmax=100)
                return cmap(norm(val))

        model_map_data = models_data["cells"]
        model_agents_pos = models_data["agents"]

        y, x = model_map_data.shape

        for j in range(y):
            for i in range(x):
                color = get_cell_color(model_map_data[j, i])
                ax.add_patch(plt.Rectangle((j, i), 1, 1, facecolor=color, edgecolor=None, alpha=alpha))

        if plot_agents:
            for (j, i) in model_agents_pos:
                ax.add_patch(plt.Circle((j, i), 1, facecolor="red", edgecolor=None, alpha=alpha))



    """task for each process - creates models, runs the simulations and returns the simulation data to the queue"""
    @staticmethod
    def _run_task(model_params: list[dict], queue: mp.Queue, stop_time: int) -> None:

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
            if model_item[2] == "normal":
                model_metric = ClosestMetric()
            else:
                model_metric = AffordanceMetric()

            model = ParkModel(agent_params=model_item[0], seed=model_item[1], metric=model_metric, park_name=model_item[3])
            model.setup()
            for _ in range(stop_time):
                model.step()
            models_data.append({"params" : model_item, "heatmap": model.heatmap, "cells": get_map_matrix(), "agents": [agent.cell.coordinate for agent in model.agents], "accuracy" : model.calculate_accuracy(), "metric" : str(model.metric)})

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

            process = mp.Process(target=GridSearch._run_task, args=(self.params[start_index: end_index], results_queue, self.stop_step))
            processes.append(process)
            process.start()

        for process in processes:
            process.join()


        final_models = []

        while not results_queue.empty():
            final_models.extend(results_queue.get())

        self.models_data = final_models

    def slice_models(self, acc_thresh: float):
        # acc_thresh max value is 1 - 100% acc
        self.models_data = [model for model in self.models_data if model['accuracy'][0] >= acc_thresh]


    """Checks whether exists the directory for plot directories and the plot directories as well"""
    @staticmethod
    def check_create_dir(directory: str,  plot_dirname: str) -> None:

        path = os.path.join(directory, plot_dirname)
        os.makedirs(path, exist_ok=True)
