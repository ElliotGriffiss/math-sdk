"""Game-specific configuration file for scratch card game"""

from src.config.config import Config
from src.config.distributions import Distribution
from src.config.config import BetMode


class GameConfig(Config):
    """Configuration class for scratch card game."""

    def __init__(self):
        super().__init__()
        self.game_id = "scratch_card"
        self.provider_numer = 0
        self.working_name = "Scratch Card Game"
    self.wincap = 2000.0
        self.win_type = "scratch"
        self.rtp = 0.9500
        self.construct_paths()

        # Game Dimensions - 4x2 grid for scratch card
        self.grid_size = (4, 2)
        
        # Required by base class
        self.num_reels = 1
        self.num_rows = [1]  # Minimal values since we don't use these
        
        # Symbol Properties
        self.symbols = ["1", "2", "5", "10", "20", "50", "100", "500", "1000"]
        self.paytable = {
            (3, "1"): 1,
            (3, "2"): 2,
            (3, "5"): 5,
            (3, "10"): 10,
            (3, "20"): 20,
            (3, "50"): 50,
            (3, "100"): 100,
            (3, "500"): 500,
            (3, "1000"): 1000
        }
        
        # Simple lookup for symbol values
        self.symbol_values = {
            "1": 1,
            "2": 2,
            "5": 5,
            "10": 10,
            "20": 20,
            "50": 50,
            "100": 100,
            "500": 500,
            "1000": 1000
        }

        # Bonus Feature Configuration
        self.bonus_spins = 5  # Number of free spins awarded
        self.bonus_multiplier = 2  # Multiplier for wins during bonus spins
        self.bonus_chance = 0.02  # 1 in 50 chance to trigger bonus
        
        # Win conditions
        self.required_matches = 3  # Number of matching symbols needed to win
        # Symbol weights for base game
        self.symbol_weights = {
            "1": 100,
            "2": 80,
            "5": 60,
            "10": 40,
            "20": 30,
            "50": 20,
            "100": 10,
            "500": 5,
            "1000": 1
        }

        # Symbol weights for bonus spins (better odds)
        self.bonus_weights = {
            "1": 80,
            "2": 70,
            "5": 50,
            "10": 35,
            "20": 25,
            "50": 15,
            "100": 8,
            "500": 3,
            "1000": 1
        }

        # Set up base reels for distribution requirements
        self.reels = {"BASE": self.symbol_weights}

        # Game modes and distributions
        normal_condition = {
            "reel_weights": {"BASE": 1},
            "symbol_weights": self.symbol_weights,
            "force_wincap": False,
            "force_freegame": False
        }

        wincap_condition = {
            "reel_weights": {"BASE": 1},
            "symbol_weights": {"1000": 1},  # Force all cells to be 1000 symbol
            "force_wincap": True,
            "force_freegame": False
        }

        zerowin_condition = {
            "reel_weights": {"BASE": 1},
            "symbol_weights": {
                "1": 1,
                "2": 1,
                "5": 1,
                "10": 1,
                "20": 1
            },
            "force_wincap": False,
            "force_freegame": False
        }

        # Bet modes configuration
        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=self.wincap,
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=self.wincap,
                        conditions=wincap_condition
                    ),
                    Distribution(
                        criteria="0",
                        quota=0.3,
                        win_criteria=0.0,
                        conditions=zerowin_condition
                    ),
                    Distribution(
                        criteria="normal",
                        quota=0.699,
                        conditions=normal_condition
                    ),
                ],
            )
        ]
