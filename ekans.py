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

SNAKE_INIT_MOVE_INTERVAL = 300
SNAKE_MIN_MOVE_INTERVAL = 50
SNAKE_SPEED_FACTOR = 0.95


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
    def __init__(self):
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(FOOD_COLOR)
        self.rect = self.image.get_rect(topleft=random_cell())

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)

    def relocate(self):
        self.rect.topleft = random_cell()


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

    def __init__(self):
        self.segments = [
            Snake.Segment(
                position=(NUM_COLS // 2 * CELL_SIZE, NUM_ROWS // 2 * CELL_SIZE),
                direction=random.choice(list(Direction)),
            )
        ]
        self.last_move_time = 0
        self.move_interval = SNAKE_INIT_MOVE_INTERVAL

    def draw(self, surface: pygame.Surface):
        for segment in self.segments:
            segment.draw(surface)

    def move(self, dt: int):
        self.last_move_time += dt

        if self.last_move_time >= self.move_interval:
            head = self.segments[0]
            front_pos = (
                head.rect.left + head.direction.value[0] * CELL_SIZE,
                head.rect.top + head.direction.value[1] * CELL_SIZE,
            )
            new_head = Snake.Segment(position=front_pos, direction=head.direction)
            self.segments.pop()
            self.segments.insert(0, new_head)
            self.last_move_time = 0

    def change_direction(self, key: int):
        head = self.segments[0]
        if key == pygame.K_UP and head.direction != Direction.DOWN:
            head.direction = Direction.UP
        elif key == pygame.K_DOWN and head.direction != Direction.UP:
            head.direction = Direction.DOWN
        elif key == pygame.K_LEFT and head.direction != Direction.RIGHT:
            head.direction = Direction.LEFT
        elif key == pygame.K_RIGHT and head.direction != Direction.LEFT:
            head.direction = Direction.RIGHT

    def grow(self):
        tail = self.segments[-1]
        back_pos = (
            tail.rect.left - tail.direction.value[0] * CELL_SIZE,
            tail.rect.top - tail.direction.value[1] * CELL_SIZE,
        )
        self.segments.append(Snake.Segment(position=back_pos, direction=tail.direction))
        self.move_interval = max(
            SNAKE_MIN_MOVE_INTERVAL, int(self.move_interval * SNAKE_SPEED_FACTOR)
        )

    def eat(self, food: Food):
        head = self.segments[0]
        return head.rect.colliderect(food.rect)

    def collide(self):
        head = self.segments[0]

        for segment in self.segments[1:]:
            if head.rect.colliderect(segment.rect):
                return True

        if (
            head.rect.left < 0
            or head.rect.left + CELL_SIZE > SCREEN_WIDTH
            or head.rect.top < 0
            or head.rect.top + CELL_SIZE > SCREEN_HEIGHT
        ):
            return True

        return False


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    running = True

    snake = Snake()
    food = Food()

    while running:
        dt = clock.tick(FRAME_RATE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            if event.type == pygame.KEYDOWN:
                snake.change_direction(event.key)

        snake.move(dt)

        if snake.eat(food):
            snake.grow()
            food.relocate()

        if snake.collide():
            running = False

        screen.fill(SCREEN_COLOR)
        snake.draw(screen)
        food.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
