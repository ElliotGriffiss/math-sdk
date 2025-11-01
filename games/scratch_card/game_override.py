from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome


class GameStateOverride(GameExecutables):
    """
    This class is is used to override or extend universal state.py functions.
    e.g: A specific game may have custom book properties to reset
    """

    def reset_book(self):
        """Reset game specific properties"""
        super().reset_book()

    def assign_special_sym_function(self):
        self.special_symbol_functions = {
            "M": [self.assign_mult_property],
            "W": [self.assign_mult_property],
        }

    def assign_mult_property(self, symbol):
        multiplier_value = get_random_outcome(
            self.get_current_distribution_conditions()["mult_values"][self.gametype]
        )
        symbol.multiplier = multiplier_value

    def check_game_repeat(self):
        if self.repeat == False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None:
                # For zero-win distribution, exact match is fine
                if win_criteria == 0 and self.final_win != 0:
                    self.repeat = True
                # For wincap distribution, ensure we hit exactly wincap
                elif win_criteria == self.config.wincap and self.final_win != self.config.wincap:
                    self.repeat = True
                # For normal distribution, no specific win amount to match
                elif win_criteria is None:
                    pass
