import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
CELL_SIZE = 40
NUM_COLS, NUM_ROWS = SCREEN_WIDTH // CELL_SIZE, SCREEN_HEIGHT // CELL_SIZE

SCREEN_COLOR = (0, 0, 0)
SNAKE_COLOR = (0, 255, 0)


class Snake:
    class Segment:
        def __init__(self, *, position: tuple[int, int]):
            self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
            self.image.fill(SNAKE_COLOR)
            self.rect = self.image.get_rect(topleft=position)

        def draw(self, surface: pygame.Surface):
            surface.blit(self.image, self.rect)

    segments: list[Segment]

    def __init__(self):
        self.segments = [
            Snake.Segment(
                position=(NUM_COLS // 2 * CELL_SIZE, NUM_ROWS // 2 * CELL_SIZE)
            )
        ]

    def draw(self, surface: pygame.Surface):
        for segment in self.segments:
            segment.draw(surface)

    # TODO: Implement actual grow logic
    def grow(self):
        tail = self.segments[-1]
        self.segments.append(
            Snake.Segment(position=(tail.rect.left + CELL_SIZE, tail.rect.top))
        )


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    running = True

    snake = Snake()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            if event.type == pygame.KEYDOWN:
                # TODO: Snake grows when it eats food
                if event.key == pygame.K_SPACE:
                    snake.grow()

        screen.fill(SCREEN_COLOR)
        snake.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
