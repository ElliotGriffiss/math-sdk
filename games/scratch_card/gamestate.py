"""Handles the state and output for a scratch card game simulation round"""

from game_override import GameStateOverride
from game_events import Event, ScratchGridEvent, ScratchWinEvent, BonusTriggeredEvent, BonusSpinEvent, BonusEndEvent, BonusSpotEvent
import random


class GameState(GameStateOverride):
    """Handle game-logic and event updates for scratch card game."""

    def __init__(self, config):
        super().__init__(config)
        self.book.events = []
        self.event_queue = self.book.events

    def run_spin(self, sim, simulation_seed=None):
        """Run a single game round"""
        self.reset_seed(sim)
        self.repeat = True
        self.attempts = 0
        max_attempts = 10000  # Safety cap to prevent infinite loops
        
        while self.repeat and self.attempts < max_attempts:
            self.attempts += 1
            self.reset_book()
            
            # Reset win manager for this attempt
            self.win_manager.reset_spin_win()
            
            # Generate main scratch card grid
            self.generate_grid()
            
            # Generate bonus spot
            self.generate_bonus_spot()
            
            # Check for wins
            self.check_wins()
            
            # Check for bonus trigger
            if self.check_bonus_trigger():
                self.run_bonus()
            
            # Don't call evaluate_finalwin inside the loop - just check_repeat
            # We need to update final_win manually for the repeat check
            self.final_win = self.win_manager.running_bet_win
            self.check_repeat()
            
            # Debug output if stuck
            if self.attempts > 100 and self.attempts % 100 == 0:
                print(f"  [DEBUG] Sim {sim}: Attempt {self.attempts}, win={self.final_win}, repeat={self.repeat}, win_criteria={self.get_current_betmode_distributions().get_win_criteria()}")
        
        # Once we're done with the repeat loop, update gametype wins and evaluate final
        self.win_manager.update_gametype_wins(self.gametype)
        self.evaluate_finalwin()
        
        if self.attempts >= max_attempts:
            print(f"  [WARNING] Sim {sim}: Hit max attempts ({max_attempts}), forcing exit with final_win={self.final_win}")
            self.repeat = False
            
        self.imprint_wins()

    def generate_grid(self, is_bonus=False):
        """Generate the scratch card grid based on symbol weights"""
        # Get the current distribution (not just the first one!)
        current_dist_conditions = self.get_current_distribution_conditions()
        
        if is_bonus:
            weights = self.config.bonus_weights
        else:
            weights = current_dist_conditions["symbol_weights"]
            
        symbols = list(weights.keys())
        symbol_weights = list(weights.values())
        
        # Generate grid_size[0] x grid_size[1] grid
        self.grid = []
        for i in range(self.config.grid_size[0]):
            row = []
            for j in range(self.config.grid_size[1]):
                symbol = random.choices(symbols, weights=symbol_weights, k=1)[0]
                row.append(symbol)
            self.grid.append(row)
        
        # Store in book for event tracking
        self.book.board = self.grid
        
        # Emit grid event
        self.event_queue.append(ScratchGridEvent(self.grid))

    def generate_bonus_spot(self):
        """Generate the bonus spot result"""
        # Don't trigger bonus when forcing specific win criteria (wincap or zero-win)
        current_dist = self.get_current_distribution_conditions()
        if current_dist.get("force_wincap", False):
            self.bonus_result = False
        else:
            # 1 in 50 chance for bonus (2%)
            self.bonus_result = random.random() < self.config.bonus_chance
        
        self.book.bonus_spot = self.bonus_result
        
        # Emit bonus spot event
        self.event_queue.append(BonusSpotEvent(self.bonus_result))

    def check_wins(self):
        """Check for winning combinations in the grid"""
        symbols_count = {}
        total_win = 0
        
        # Count all symbols in the grid
        for row in self.grid:
            for symbol in row:
                symbols_count[symbol] = symbols_count.get(symbol, 0) + 1
        
        # Check for matches
        for symbol, count in symbols_count.items():
            if count >= self.config.required_matches:
                win_amount = self.config.symbol_values[symbol]
                # Multiply by current bet cost (bet_amount not set on GameState by default)
                win_total = win_amount * self.get_current_betmode().get_cost()
                
                # Apply bonus multiplier if in bonus mode
                if hasattr(self, 'in_bonus') and self.in_bonus:
                    win_total *= self.config.bonus_multiplier
                
                total_win += win_total
                
                # Record win via events (book doesn't have a 'wins' list)
                win_data = {
                    "symbol": symbol,
                    "matches": count,
                    "amount": win_total,
                }
                
                # Emit win event
                self.event_queue.append(ScratchWinEvent(symbol, count, win_total))
        
        self.win_amount = total_win
        
        # Update win_manager with the win amount
        # Only update spinwin here, don't call update_gametype_wins yet
        # as that will be handled in evaluate_finalwin
        self.win_manager.update_spinwin(total_win)
        
        # Debug output for wincap attempts
        current_dist = self.get_current_distribution_conditions()
        if current_dist.get("force_wincap", False) and hasattr(self, 'attempts'):
            if self.attempts <= 5 or self.attempts % 1000 == 0:
                print(f"  [WIN_DEBUG] Grid: {self.grid}, Counts: {symbols_count}, Win: {total_win}, WinManager: {self.win_manager.running_bet_win}")

    def check_bonus_trigger(self):
        """Check if bonus feature is triggered"""
        return self.bonus_result

    def run_bonus(self):
        """Run the bonus feature with free spins"""
        # Route to shared freespin flow
        self.run_freespin()

    def run_freespin(self):
        """Run the free spins feature using engine-aligned flow and events"""
        # Emit start event
        self.event_queue.append(BonusTriggeredEvent(self.config.bonus_spins))
        # Switch to freegame mode and reset spin win
        self.reset_fs_spin()
        self.in_bonus = True
        total_bonus_win = 0

        for spin in range(self.config.bonus_spins):
            # Emit engine fs update and custom event
            self.update_freespin()
            self.event_queue.append(BonusSpinEvent(spin + 1, self.config.bonus_spins))

            # Generate and evaluate bonus spin
            self.generate_grid(is_bonus=True)
            self.check_wins()
            # Attribute this spin to freegame bucket
            self.win_manager.update_gametype_wins(self.gametype)
            total_bonus_win += self.win_amount

        # End of freegame
        self.end_freespin()
        self.event_queue.append(BonusEndEvent(total_bonus_win))
        self.in_bonus = False
        self.triggered_freegame = True

        # Record bonus details in book
        self.book.bonus = {
            "spins": self.config.bonus_spins,
            "total_win": total_bonus_win
        }

    def check_fs_condition(self):
        """Implement required method - not used in scratch card"""
        return False

    def evaluate_lines_board(self):
        """Implement required method - not used in scratch card"""
        pass
