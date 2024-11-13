import enum
import random

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


def random_cell():
    col = random.randint(0, NUM_COLS - 1)
    row = random.randint(0, NUM_ROWS - 1)
    return (col * CELL_SIZE, row * CELL_SIZE)


class Direction(enum.Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class Food:
    def __init__(self, *, position: tuple[int, int]):
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(FOOD_COLOR)
        self.rect = self.image.get_rect(topleft=position)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)

    def relocate(self, snake: "Snake"):
        snake_segments = {segment.rect.topleft for segment in snake.segments}
        available_pos = [pos for pos in ALL_POSITIONS if pos not in snake_segments]
        self.rect.topleft = random.choice(available_pos)


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

    def __init__(self, *, position: tuple[int, int]):
        self.segments = [
            Snake.Segment(
                position=position,
                direction=random.choice(list(Direction)),
            )
        ]
        self.last_move_time = 0
        self.move_interval = SNAKE_INIT_MOVE_INTERVAL
        self.next_direction = self.segments[0].direction

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
        if key in (pygame.K_UP, pygame.K_w) and self.head.direction != Direction.DOWN:
            self.next_direction = Direction.UP
        elif key in (pygame.K_DOWN, pygame.K_s) and self.head.direction != Direction.UP:
            self.next_direction = Direction.DOWN
        elif (
            key in (pygame.K_LEFT, pygame.K_a)
            and self.head.direction != Direction.RIGHT
        ):
            self.next_direction = Direction.LEFT
        elif (
            key in (pygame.K_RIGHT, pygame.K_d)
            and self.head.direction != Direction.LEFT
        ):
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


class Score:
    value: int

    def __init__(self):
        self.value = 0
        self.font = pygame.font.Font(None, 32)
        self.update_image()

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)

    def increase(self):
        self.value += 1
        self.update_image()

    def update_image(self):
        msg = f"Score: {self.value}"
        self.image = self.font.render(msg, 0, SCORE_COLOR)
        self.rect = self.image.get_rect(topleft=(16, SCREEN_HEIGHT - 40))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    running = True

    snake = Snake(position=(NUM_COLS // 2 * CELL_SIZE, NUM_ROWS // 2 * CELL_SIZE))
    food = Food(
        position=random.choice(
            [pos for pos in ALL_POSITIONS if pos != snake.head.rect.topleft]
        )
    )
    score = Score()

    while running:
        dt = clock.tick(FRAME_RATE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE,
                pygame.K_q,
            ):
                running = False

            if event.type == pygame.KEYDOWN:
                snake.change_direction(event.key)

        snake.move(dt)

        if snake.eat(food):
            snake.grow()
            food.relocate(snake)
            score.increase()

        if snake.collide():
            running = False

        screen.fill(SCREEN_COLOR)
        snake.draw(screen)
        food.draw(screen)
        score.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
