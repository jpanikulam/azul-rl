"""Implement game state for the board game Azul"""
import random
from matplotlib import pyplot as plt
import matplotlib.patches as patches


def state_to_vec(state):
    """
    Convert a state to a vector.
    """
    return NotImplemented


class GameConfig(object):
    def __init__(self):
        self.players = 1
        self.round = 1
        self.n_colors = 2
        self.n_factory_displays = 1
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
        self.curr_step = 0

    def draw(self):
        colors = ['r', 'g', 'b', 'y', 'c', 'm']

        # plt.figure("Factory Displays")
        # ax = plt.gca()
        # for x, factory_display in enumerate(self.factory_displays):
        #     for y, count in enumerate(factory_display):
        #         scale= (1.0 / len(factory_display))
        #         rect = patches.Rectangle(
        #             (x*scale + 0.05 * scale,
        #             y*scale + 0.05 * scale),
        #             0.9*scale,
        #             0.9*scale,
        #             linewidth=1,
        #             edgecolor=color,
        #             facecolor=color)
        #         ax.add_patch(rect)

        for n, player in enumerate(self.players):
            plt.figure(f"Player {n}")
            ax = plt.gca()
            for x, board_row in enumerate(player['board']):
                for y, count in enumerate(board_row):
                    color = colors[(y + x) % len(board_row)]
                    scale= (1.0 / len(board_row))

                    if count != 0:
                        rect = patches.Rectangle(
                            (x*scale + 0.05 * scale,
                            y*scale + 0.05 * scale),
                            0.9*scale,
                            0.9*scale,
                            linewidth=1,
                            edgecolor=color,
                            facecolor=color)
                        ax.add_patch(rect)
                    else:
                        rect = patches.Rectangle(
                            (x*scale + 0.05 * scale,
                            y*scale + 0.05 * scale),
                            0.9*scale,
                            0.9*scale,
                            linewidth=1,
                            edgecolor=color,
                            facecolor='none')
                        ax.add_patch(rect)


    def available_actions(self, cfg: GameConfig):
        """Generate a list of available of actions

        Simplifications:
            - There is only one player
            - There is only one factory display

        Victory:
            - The learner learns not to play illegal moves
        """
        player_idx = self.curr_step % len(self.players)
        actions = []
        for factory_display in range(len(self.factory_displays)):
            for source_color, count in enumerate(self.factory_displays[factory_display]):
                if count != 0:
                    for destination_color in range(cfg.n_colors):
                        (pending_color, count) = self.players[player_idx]['pending'][destination_color]
                        nothing_pending = pending_color == -1
                        pending_matches = pending_color == source_color
                        board_spot_unoccupied = self.players[player_idx]['board'][pending_color][source_color] == 0
                        if (nothing_pending or pending_matches) and board_spot_unoccupied:
                            actions.append((factory_display, source_color, destination_color))
        return actions


    def grab_and_place_tile(self, factory_display, color, row):
        player_idx = self.curr_step % len(self.players)

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
        self.curr_step += 1
        return {'success': True}

    def step(self, cfg: GameConfig):
        for idx, player in enumerate(self.players):
            for row_idx, row in enumerate(player['pending']):
                (color, count) = row
                if count == color + 1:
                    print(f"Stepping {row_idx} {color}")
                    self.players[idx]['board'][row_idx][(row_idx + color) % cfg.n_colors] += 1
                    self.players[idx]['pending'][row_idx] = (-1, 0)


game_cfg = GameConfig()
game_state = BoardState(game_cfg)
game_state.start_round(game_cfg)
game_state.print()
print(game_state.grab_and_place_tile(factory_display=0, color=0, row=1))
game_state.print()
print(game_state.available_actions(cfg=game_cfg))
game_state.step(cfg=game_cfg)
game_state.print()
game_state.draw()
plt.show()

# observations (everything is row major)
# array: num colors * num displays
#     domain: [0, num_tiles_per_factory_display)
# array: flat list of bools
# pending: num_colors * num_colors