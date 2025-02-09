"""Implement game state for the board game Azul"""
import random

def state_to_vec(state):
    """
    Convert a state to a vector.
    """
    return NotImplemented


class GameConfig(object):
    def __init__(self):
        self.players = 2
        self.round = 1
        self.n_colors = 2
        self.n_factory_displays = 2
        self.n_tiles_per_factory_display = 2

def create_empty_board(cfg: GameConfig):
    """
    Create an empty board.
    """
    return [[0 for _ in range(cfg.n_colors)] for _ in range(cfg.n_colors)]


class BoardState(object):
    def __init__(self, cfg: GameConfig):
        self.players = []
        for n in range(cfg.players):
            self.players.append({
                'board': create_empty_board(cfg),
                'pending': [(-1, 0) for _ in range(cfg.n_colors)],
            })

        self.factory_displays = []

    def print(self):
        print("Players...")
        for player in self.players:
            print(f"  {player}")
        print("Factory Displays...")
        for factory_display in self.factory_displays:
            print(f"  {factory_display}")

    def start_round(self, cfg: GameConfig):
        # Populate the factory displays with N

        self.factory_displays = [
            [2, 0],
            [1, 1],
        ]
        self.step = 0

    def grab_and_place_tile(self, factory_display, color, row):
        player_idx = self.step % len(self.players)

        if factory_display < 0 or factory_display >= len(self.factory_displays):
            return {'error': 'Invalid factory display'}
        chosen_display = self.factory_displays[factory_display]

        n_added = chosen_display[color]

        if n_added == 0:
            return {'error': 'Tile not present in display'}

        chosen_display[color] = 0

        (current_tile_id, current_count) = self.players[player_idx]['pending'][row]

        if current_tile_id != -1 and current_tile_id != color:
            return {'error': 'Tile not present in location'}

        if current_count > row + 1:
            return {'error': 'No room for tile'}

        self.players[player_idx]['pending'][row] = (color, current_count + n_added)
        self.step += 1
        return {'success': True}


game_cfg = GameConfig()
game_state = BoardState(game_cfg)
game_state.start_round(game_cfg)
game_state.print()
print(game_state.grab_and_place_tile(factory_display=0, color=0, row=1))

game_state.print()