"""Events for the scratch card game"""

class Event:
    """Base event class"""
    def __init__(self):
        self.index = 0
        
class ScratchGridEvent(Event):
    """Event for displaying the scratch card grid"""
    def __init__(self, grid):
        super().__init__()
        self.type = "scratch_grid"
        self.grid = grid

class ScratchWinEvent(Event):
    """Event for scratch card wins"""
    def __init__(self, symbol, matches, amount):
        super().__init__()
        self.type = "scratch_win"
        self.symbol = symbol
        self.matches = matches
        self.amount = int(amount * 100)  # Convert to cents

class BonusSpotEvent(Event):
    """Event for revealing the bonus spot"""
    def __init__(self, is_bonus):
        super().__init__()
        self.type = "bonus_spot"
        self.is_bonus = is_bonus

class BonusTriggeredEvent(Event):
    """Event for when bonus free spins are triggered"""
    def __init__(self, num_spins):
        super().__init__()
        self.type = "bonus_triggered"
        self.num_spins = num_spins

class BonusSpinEvent(Event):
    """Event for each bonus spin"""
    def __init__(self, spin_number, total_spins):
        super().__init__()
        self.type = "bonus_spin"
        self.spin_number = spin_number
        self.total_spins = total_spins
        
class BonusEndEvent(Event):
    """Event for when bonus feature ends"""
    def __init__(self, total_bonus_win):
        super().__init__()
        self.type = "bonus_end"
        self.total_bonus_win = int(total_bonus_win * 100)  # Convert to cents
