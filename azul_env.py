import gymnasium as gym
import numpy as np
from gymnasium import spaces
from azul import GameConfig
from gymnasium.spaces import Dict


class AzulEnv(gym.Env):
    """Custom environment that follows gym interface."""

    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self, cfg: GameConfig):
        super().__init__()
        # Define action and observation space
        self.action_space = spaces.MultiDiscrete([cfg.n_factory_displays, cfg.n_colors, cfg.n_colors])

        obs_space_factory = spaces.MultiDiscrete(
            [cfg.n_tiles_per_factory_display] * cfg.n_colors * cfg.n_factory_displays
        )
        obs_space_board = spaces.MultiBinary(cfg.n_colors * cfg.n_colors)
        # [1, 1, 1, 1, 1, 2, 2, 2, 2, 2]
        # count of how many tiles for a given color are on that row
        obs_space_pending = spaces.MultiDiscrete(
            list(np.array([[i + 1] * cfg.n_colors for i in range(cfg.n_rows)]).flatten())
        )

        self.observation_space = Dict(
            {"factory": obs_space_factory, "board": obs_space_board, "pending": obs_space_pending}
        )

    def _game_state_to_obs(self, game_state: BoardState):
        factory = np.array(game_state.factory_displays).flatten()  # N colors x N factory displays
        board = np.array(game_state.players[0]["board"]).flatten()
        pending = [0] * cfg.n_colors * cfg.n_rows  # count of each color for each row

        for row_idx, row_data in enumerate(game_state.players[0]["pending"]):
            (color, count) = row_data
            if color > -1:
                pending[row_idx * cfg.n_colors + color] += count

        return {"factory": factory, "board": board, "pending": pending}

    def step(self, action):
        factory, color, pending_row = action

        # Play azul with the game engine

        observation = self._game_state_to_obs(self.game_state)
        print(f"Action: {action}")
        print(f"Observation: {observation}")

        reward = 10
        terminated, truncated, info = [None] * 3

        return observation, reward, terminated, truncated, info

    def reset(self, seed=None, options=None):
        game_cfg = GameConfig()
        game_state = BoardState(game_cfg)
        game_state.start_round(game_cfg)

        self.game_state = game_state


        observation, info = [None] * 2
        return observation, info

    def render(self): ...

    def close(self): ...


env = AzulEnv(GameConfig())
env.step(env.action_space.sample())

# # Instantiate the env
# env = AzulGymEnv(arg1, ...)

# # Define and Train the agent
# model = A2C("CnnPolicy", env).learn(total_timesteps=1000)
# model = PPO(
#     "MlpPolicy",
#     env,
#     verbose=1,
#     n_steps=PPO_NUM_STEPS,
#     batch_size=PPO_BATCH_SIZE,
#     n_epochs=PPO_NUM_EPOCHS,
#     tensorboard_log="ppo_logs/",
# )
