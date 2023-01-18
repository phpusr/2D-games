import pathlib
import sys

import pygame
from pygame.font import Font

from logic import Snake, SnakeDirection, SnakeError

WIDTH_BLOCK_COUNT = 50
HEIGHT_BLOCK_COUNT = 30
BLOCK_WIDTH = 20
MARGIN_BLOCK = 3

WIDTH = 1000
HEIGHT = 600
FPS = 60

SNAKE_COLOR = (200, 10, 10)


font_cache = dict()


def get_font(size: int, bold: bool = False) -> Font:
    font_cache_name = f'{size}{"-bold" if bold else ""}'
    font = font_cache.get(font_cache_name)
    if font:
        return font

    path = pathlib.Path(__file__).parent.parent.resolve()
    font_name = 'Oswald-Bold.ttf' if bold else 'Oswald-Regular.ttf'
    font = pygame.font.Font(path / 'shared/fonts' / font_name, size)
    font_cache[font_cache_name] = font
    return font


class SnakeGame:
    def __init__(self):
        # Init data
        self.game_over = False
        self.prev_direction = SnakeDirection.left
        self.current_direction = self.prev_direction
        self.snake = Snake(WIDTH_BLOCK_COUNT, HEIGHT_BLOCK_COUNT, self.current_direction)
        # Init GUI
        pygame.init()
        pygame.display.set_caption('Snake')
        self.sc = pygame.display.set_mode((WIDTH, HEIGHT))

    def start(self):
        clock = pygame.time.Clock()
        self.restart()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.exit()
                    elif event.key == pygame.K_r:
                        self.restart()
                    elif event.key == pygame.K_UP:
                        self.current_direction = SnakeDirection.up
                    elif event.key == pygame.K_DOWN:
                        self.current_direction = SnakeDirection.down
                    elif event.key == pygame.K_LEFT:
                        self.current_direction = SnakeDirection.left
                    elif event.key == pygame.K_RIGHT:
                        self.current_direction = SnakeDirection.right
            
            self.change_direction()
            
            try:
                self.snake.move()
            except SnakeError:
                self.game_over = True

            self.draw_gui()
            clock.tick(FPS)
            pygame.time.wait(1000 - self.snake.speed * 100)

    def restart(self):
        self.current_direction = None
        self.snake = Snake(WIDTH_BLOCK_COUNT, HEIGHT_BLOCK_COUNT)

    def change_direction(self):
        if SnakeDirection.can_change(self.prev_direction, self.current_direction):
            self.snake.change_direction(self.current_direction)
            self.prev_direction = self.current_direction

    def draw_gui(self):
        if self.game_over:
            self.draw_game_over()
            pygame.display.update()
            return

        self.sc.fill((10, 30, 100))
        self.draw_snake()
        pygame.display.update()

    def draw_game_over(self):
        text = get_font(72).render('Game over', True, (0, 0, 0), (200, 200, 200))
        text_rect = text.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        self.sc.blit(text, text_rect)

    def draw_snake(self):
        block_index = 0
        for block in self.snake.blocks:
            xcor = block.xcor * BLOCK_WIDTH + (block.xcor + 1) * MARGIN_BLOCK
            ycor = block.ycor * BLOCK_WIDTH + (block.ycor + 1) * MARGIN_BLOCK
            pygame.draw.rect(self.sc, (200 - (block_index * 50) % 199, 100, 10), (xcor, ycor, BLOCK_WIDTH, BLOCK_WIDTH))
            block_index += 1

    def exit(self):
        pygame.quit()
        sys.exit(0)


if __name__ == '__main__':
    SnakeGame().start()
