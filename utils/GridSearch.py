import os
import multiprocessing as mp
from model import ParkModel
import random
import seaborn as sns
import matplotlib.pyplot as plt

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


        for i, model in enumerate(self.models_data):

            plt.figure(figsize=(20, 14), dpi=300)

            model_heatmap_data = model[1]

            sns.heatmap(
                data=model_heatmap_data,
                cmap="Oranges",
                vmin=0,
                vmax=model_heatmap_data.max(),
            )

            print(f"Saving to {self.directory}/{model[0]}{i}.png")
            plt.title(f"{model[0]}")
            plt.savefig(f"{self.directory}/{model[0]}{i}.png")
            plt.close()

    def _model_task(self, model_params: list[dict], queue: mp.Queue) -> None:
        models_data = []
        for i, model_item in enumerate(model_params):
            model = ParkModel(agent_params=model_item)
            model.setup()
            for _ in range(self.stop_step):
                model.step()
            models_data.append([model_item, model.heatmap])

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