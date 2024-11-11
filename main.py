import enum
import random

import pygame

FRAME_RATE = 60  # frames per second
CELL_SIZE = 40  # pixels
SCREENRECT = pygame.Rect(0, 0, 800, 600)


class Direction(enum.Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class Snake(pygame.sprite.Sprite):
    def __init__(self, *groups) -> None:
        super().__init__(*groups)
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect(
            topleft=(
                SCREENRECT.width // (2 * CELL_SIZE) * CELL_SIZE,
                SCREENRECT.height // (2 * CELL_SIZE) * CELL_SIZE,
            )
        )
        self.direction = random.choice(list(Direction))
        self.speed = 2  # cells per second
        self.frame = 0

    def update(self) -> None:
        dirx, diry = self.direction.value
        dx = dirx * CELL_SIZE
        dy = diry * CELL_SIZE

        if self.frame >= (FRAME_RATE // self.speed):
            self.rect.move_ip(dx, dy)
            self.frame = 0

        self.frame += 1

    def set_direction(self, key: int) -> None:
        if key == pygame.K_UP:
            self.direction = Direction.UP
        elif key == pygame.K_DOWN:
            self.direction = Direction.DOWN
        elif key == pygame.K_LEFT:
            self.direction = Direction.LEFT
        elif key == pygame.K_RIGHT:
            self.direction = Direction.RIGHT

    def collide_wall(self):
        return not SCREENRECT.contains(self.rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREENRECT.width, SCREENRECT.height))
    clock = pygame.time.Clock()
    running = True

    all_sprites = pygame.sprite.Group()
    snake = Snake(all_sprites)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False

                snake.set_direction(event.key)

        all_sprites.update()

        if snake.collide_wall():
            running = False

        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        pygame.display.flip()

        clock.tick(FRAME_RATE)

    pygame.quit()


if __name__ == "__main__":
    main()
