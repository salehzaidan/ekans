import enum

import gymnasium as gym
import numpy as np
import pygame

FRAME_RATE = 60
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CELL_SIZE = 40
NUM_COLS, NUM_ROWS = SCREEN_WIDTH // CELL_SIZE, SCREEN_HEIGHT // CELL_SIZE

SCREEN_COLOR = (0, 0, 0)
SNAKE_COLOR = (0, 255, 0)
FOOD_COLOR = (255, 0, 0)
SCORE_COLOR = (255, 255, 255)

SNAKE_INIT_MOVE_INTERVAL = 300
SNAKE_MIN_MOVE_INTERVAL = 50
SNAKE_SPEED_FACTOR = 0.95

ALL_POSITIONS = [
    (col * CELL_SIZE, row * CELL_SIZE)
    for col in range(NUM_COLS)
    for row in range(NUM_ROWS)
]

FRAME_REWARD = -0.01
EAT_REWARD = 1.0
COLLIDE_REWARD = -10.0


class Direction(enum.Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class Food:
    def __init__(self, *, position: tuple[int, int], rng: np.random.Generator):
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(FOOD_COLOR)
        self.rect = self.image.get_rect(topleft=position)
        self.rng = rng

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)

    def relocate(self, snake: "Snake"):
        snake_segments = {segment.rect.topleft for segment in snake.segments}
        available_pos = [pos for pos in ALL_POSITIONS if pos not in snake_segments]
        self.rect.topleft = self.rng.choice(available_pos)


class Snake:
    class Segment:
        def __init__(self, *, position: tuple[int, int], direction: Direction):
            self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
            self.image.fill(SNAKE_COLOR)
            self.rect = self.image.get_rect(topleft=position)
            self.direction = direction

        def draw(self, surface: pygame.Surface):
            surface.blit(self.image, self.rect)

    segments: list[Segment]
    last_move_time: int
    move_interval: int
    next_direction: Direction

    def __init__(self, *, position: tuple[int, int], rng: np.random.Generator):
        self.segments = [
            Snake.Segment(
                position=position,
                direction=rng.choice(list(Direction)),  # type: ignore
            )
        ]
        self.last_move_time = 0
        self.move_interval = SNAKE_INIT_MOVE_INTERVAL
        self.next_direction = self.segments[0].direction
        self.rng = rng

    def draw(self, surface: pygame.Surface):
        for segment in self.segments:
            segment.draw(surface)

    @property
    def head(self):
        return self.segments[0]

    @property
    def tail(self):
        return self.segments[-1]

    def move(self, dt: int):
        self.last_move_time += dt

        if self.last_move_time >= self.move_interval:
            self.head.direction = self.next_direction
            front_pos = (
                self.head.rect.left + self.head.direction.value[0] * CELL_SIZE,
                self.head.rect.top + self.head.direction.value[1] * CELL_SIZE,
            )
            new_head = Snake.Segment(position=front_pos, direction=self.head.direction)
            self.segments.pop()
            self.segments.insert(0, new_head)
            self.last_move_time = 0

    def change_direction(self, key: int):
        if key == 0 and self.head.direction != Direction.DOWN:
            self.next_direction = Direction.UP
        elif key == 1 and self.head.direction != Direction.UP:
            self.next_direction = Direction.DOWN
        elif key == 2 and self.head.direction != Direction.RIGHT:
            self.next_direction = Direction.LEFT
        elif key == 3 and self.head.direction != Direction.LEFT:
            self.next_direction = Direction.RIGHT

    def grow(self):
        back_pos = (
            self.tail.rect.left - self.tail.direction.value[0] * CELL_SIZE,
            self.tail.rect.top - self.tail.direction.value[1] * CELL_SIZE,
        )
        self.segments.append(
            Snake.Segment(position=back_pos, direction=self.tail.direction)
        )
        self.move_interval = max(
            SNAKE_MIN_MOVE_INTERVAL, int(self.move_interval * SNAKE_SPEED_FACTOR)
        )

    def eat(self, food: Food):
        head = self.segments[0]
        return head.rect.colliderect(food.rect)

    def collide(self):
        for segment in self.segments[1:]:
            if self.head.rect.colliderect(segment.rect):
                return True

        if (
            self.head.rect.left < 0
            or self.head.rect.left + CELL_SIZE > SCREEN_WIDTH
            or self.head.rect.top < 0
            or self.head.rect.top + CELL_SIZE > SCREEN_HEIGHT
        ):
            return True

        return False

    def reset(self, position: tuple[int, int], direction: Direction):
        self.segments = [Snake.Segment(position=position, direction=direction)]
        self.last_move_time = 0
        self.move_interval = SNAKE_INIT_MOVE_INTERVAL
        self.next_direction = self.segments[0].direction


class Score:
    value: int

    def __init__(self):
        self.value = 0
        self.font = None

    def draw(self, surface: pygame.Surface):
        if self.font is None:
            self.font = pygame.font.Font(None, 32)

        self.update_image()
        surface.blit(self.image, self.rect)

    def increase(self):
        self.value += 1

    def update_image(self):
        assert self.font is not None
        msg = f"Score: {self.value}"
        self.image = self.font.render(msg, 0, SCORE_COLOR)
        self.rect = self.image.get_rect(topleft=(16, SCREEN_HEIGHT - 40))


class EkansEnv(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": FRAME_RATE}

    def __init__(self, render_mode: str | None = None):
        self.observation_space = gym.spaces.Box(
            0, 4, (NUM_ROWS, NUM_COLS), dtype=np.int8
        )
        self.action_space = gym.spaces.Discrete(4)
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        self.screen = None
        self.clock = None

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        _ = options
        super().reset(seed=seed)
        self.snake = Snake(
            position=(NUM_COLS // 2 * CELL_SIZE, NUM_ROWS // 2 * CELL_SIZE),
            rng=self.np_random,
        )
        self.food = Food(
            position=self.np_random.choice(
                [pos for pos in ALL_POSITIONS if pos != self.snake.head.rect.topleft]
            ),
            rng=self.np_random,
        )
        self.score = Score()
        self.reward = 0.0

        if self.render_mode == "human":
            self.render_frame()

        return self.get_observation(), {}

    def step(self, action: int):
        dt = 1000 // FRAME_RATE
        if self.render_mode == "human":
            dt = self.render_frame()
            assert type(dt) is int

        self.snake.change_direction(action)

        self.snake.move(dt)
        terminated = self.snake.collide()
        truncated = False
        self.reward = FRAME_REWARD

        if self.snake.eat(self.food):
            self.reward += EAT_REWARD
            self.snake.grow()
            self.food.relocate(self.snake)
            self.score.increase()
        elif terminated:
            self.reward -= COLLIDE_REWARD

        return self.get_observation(), self.reward, terminated, truncated, {}

    def render(self):
        if self.render_mode == "rgb_array":
            return self.render_frame()

    def render_frame(self):
        pygame.font.init()

        if self.screen is None and self.render_mode == "human":
            pygame.init()
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        if self.clock is None and self.render_mode == "human":
            self.clock = pygame.time.Clock()

        canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        canvas.fill(SCREEN_COLOR)
        self.snake.draw(canvas)
        self.food.draw(canvas)

        if self.render_mode == "human":
            self.score.draw(canvas)
            assert self.screen is not None and self.clock is not None
            self.screen.blit(canvas, canvas.get_rect())
            pygame.display.flip()
            return self.clock.tick(FRAME_RATE)
        else:
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )

    def close(self):
        if self.screen is not None:
            pygame.quit()

    def get_observation(self):
        obs = np.zeros((NUM_ROWS, NUM_COLS), dtype=np.int8)

        x = (self.snake.head.rect.left - 1) // CELL_SIZE
        y = (self.snake.head.rect.top - 1) // CELL_SIZE
        obs[y][x] = 1

        for segment in self.snake.segments[1:-1]:
            x = (segment.rect.left - 1) // CELL_SIZE
            y = (segment.rect.top - 1) // CELL_SIZE

            if 0 <= x < NUM_COLS and 0 <= y < NUM_ROWS:
                obs[y][x] = 2

        x = (self.snake.tail.rect.left - 1) // CELL_SIZE
        y = (self.snake.tail.rect.top - 1) // CELL_SIZE
        obs[y][x] = 3

        x = (self.food.rect.left - 1) // CELL_SIZE
        y = (self.food.rect.top - 1) // CELL_SIZE
        obs[y][x] = 4

        return obs


gym.register("Ekans", "ekans:EkansEnv")


def main():
    action = -1

    def register_input():
        nonlocal action, quit, restart

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    action = 0
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    action = 1
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    action = 2
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    action = 3
                elif event.key == pygame.K_RETURN:
                    restart = True
                elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                    quit = True

            elif event.type == pygame.QUIT:
                quit = True

    env = gym.make("Ekans", render_mode="human")
    quit = False

    while not quit:
        env.reset()
        total_reward = 0.0
        steps = 0
        restart = False

        while True:
            register_input()
            s, r, terminated, truncated, info = env.step(action)
            total_reward += r  # type: ignore
            print(f"Step={steps}   Total Reward={total_reward:+0.2f}")
            steps += 1
            if terminated or truncated or restart or quit:
                break

    env.close()


if __name__ == "__main__":
    main()
