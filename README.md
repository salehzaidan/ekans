# Ekans

Snake game Gymnasium environment.

## Prerequisites

- Python 3.13

## Action Space

The actions are to change the snake direction:

- 0: Move up
- 1: Move down
- 2: Move left
- 3: Move right

## Observation Space

An 800x600 grid array with cell values ranging from 0 to 2, defined as follows:

- 0: Empty cell
- 1: Snake segment
- 2: Food

## Rewards

The reward is -0.01 every frame and +1 for every food eaten by the snake.

## Starting State

The snake begins with a single segment positioned at the center of the grid, while the food is randomly placed on the grid.

## Episode Termination

The episode ends if the snake collides with one of its own segments or moves out of the window boundaries.

## Arguments

```python
>>> import gymnasium as gym
>>> import ekans
>>> env = gym.make("Ekans", render_mode="rgb_array") # "rgb_array" and "human" render modes are available
>>> env
<OrderEnforcing<PassiveEnvChecker<EkansEnv<Ekans>>>>
```

## Play Manually

You can run the environment manually by executing the module directly

```sh
python -m ekans
```

The actions are mapped to the WASD button and the arrow buttons. Press Esc or Q to quit and Enter to restart the episode.
