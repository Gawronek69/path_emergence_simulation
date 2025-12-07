from utils.GridSearch import GridSearch

if __name__ == "__main__":
    grid = GridSearch(
        samples = 100,
        n_workers = 6,
        stop_step = 1000,
        metric = ["normal", "affordance", "balanced", "mixed"],
        parks = ["blackheath"],
        seeds = [1, 10, 18, 32, 42, 69, 23, 33, 45, 54, 3],
        distance = [7, 8, 9, 10, 11, 12, 13, 14, 15],
        angle = [80, 90, 100, 110, 120, 130, 140, 150],
        tile_weight = [1, 0.975, 0.95, 0.925, 0.90, 0.875, 0.85],
        distance_weight = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6]
    )
    grid.run_models()
    grid.slice_models(0.1)
    grid.get_acc()
    grid.plot_maps_heats()
