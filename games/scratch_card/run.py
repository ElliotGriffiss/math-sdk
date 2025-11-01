"""Main file for running scratch card game simulations."""

from gamestate import GameState
from game_config import GameConfig
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs
from uploads.aws_upload import upload_to_aws

if __name__ == "__main__":
    # Simulation parameters
    num_threads = 10
    batching_size = 50000
    compression = False
    profiling = False

    # Number of simulations to run for each mode
    num_sim_args = {
        "base": 1000,  # Run 1000 simulations for testing
    }

    # Run conditions
    run_conditions = {
        "run_sims": True,     # Run simulations
        "upload_data": False,  # Don't upload to AWS during testing
    }
    target_modes = ["base"]

    # Initialize game
    config = GameConfig()
    gamestate = GameState(config)

    # Run simulations if enabled
    if run_conditions["run_sims"]:
        create_books(
            gamestate,
            config,
            num_sim_args,
            batching_size,
            num_threads,
            compression,
            profiling,
        )

    # Generate configuration files
    generate_configs(gamestate)

    # Upload data to AWS if enabled
    if run_conditions["upload_data"]:
        upload_items = {
            "books": True,
            "config_files": True,
            "force_files": True,
        }
        upload_to_aws(
            gamestate,
            target_modes,
            upload_items,
        )
