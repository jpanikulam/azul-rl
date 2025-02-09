import gymnasium as gym
import numpy as np
from gymnasium import spaces
from azul import GameConfig, BoardState
from gymnasium.spaces import Dict
import random
from stable_baselines3 import PPO


class AzulEnv(gym.Env):
    """Custom environment that follows gym interface."""

    metadata = {"render_modes": ["human"], "render_fps": 30}

    def __init__(self, cfg: GameConfig):
        super().__init__()
        self.cfg = cfg

        # Define action and observation space
        self.action_space = spaces.MultiDiscrete([cfg.n_factory_displays, cfg.n_colors, cfg.n_colors])

        obs_space_factory = spaces.MultiDiscrete(
            [cfg.n_tiles_per_factory_display + 1] * cfg.n_colors * cfg.n_factory_displays
        )
        obs_space_board = spaces.MultiBinary(cfg.n_colors * cfg.n_colors)
        # [2, 2, 2, 2, 2, 3, 3, 3, 3, 3]
        # count of how many tiles for a given color are on that row
        obs_space_pending = spaces.MultiDiscrete(
            list(np.array([[i + 2] * cfg.n_colors for i in range(cfg.n_rows)]).flatten())
        )

        self.observation_space = Dict(
            {"factory": obs_space_factory, "board": obs_space_board, "pending": obs_space_pending}
        )

        # print(self.observation_space)
        # exit(0)

    def _game_state_to_obs(self, game_state: BoardState):
        factory = np.array(game_state.factory_displays).flatten()  # N colors x N factory displays
        board = np.array(game_state.players[0]["board"]).flatten()
        pending = [0] * self.cfg.n_colors * self.cfg.n_rows  # count of each color for each row

        for row_idx, row_data in enumerate(game_state.players[0]["pending"]):
            (color, count) = row_data
            if color > -1:
                pending[row_idx * self.cfg.n_colors + color] += count

        return {"factory": factory, "board": board, "pending": pending}

    def step(self, action):
        factory, color, pending_row = action

        # Do the action
        action_success, reason = self.game_state.grab_and_place_tile(
            factory_display=factory, color=color, destination_row=pending_row
        )

        # Get the observation
        observation = self._game_state_to_obs(self.game_state)

        # Calculate the reward
        reward = 1 if action_success else -1

        print(f"Action: {action}")
        print(f"Observation: {observation}")
        print(f"Reward: {reward}, {reason}")

        terminated = self.game_state.is_factory_empty()

        truncated = False
        info = {}

        return observation, reward, terminated, truncated, info

    def reset(self, seed=None, options=None):
        # random.seed(seed)

        print("Resetting game\n\n")

        game_cfg = GameConfig()
        game_state = BoardState(game_cfg)
        game_state.start_round(game_cfg)

        self.game_state = game_state

        info = {}
        observation = self._game_state_to_obs(self.game_state)
        print(f"Observation: {observation}")

        return observation, info

    def render(self): ...

    def close(self): ...


if __name__ == "__main__":

    env = AzulEnv(GameConfig())

    model = PPO(
        "MultiInputPolicy",
        env,
        verbose=1,
        # n_steps=PPO_NUM_STEPS,
        # batch_size=PPO_BATCH_SIZE,
        # n_epochs=PPO_NUM_EPOCHS,
        tensorboard_log="ppo_logs/",
    )

    env.reset()
    model.learn(total_timesteps=100000)
    model.save("Azul")
