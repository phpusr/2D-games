import json
import random
import sys

import pygame
from pygame.surface import Surface

FPS = 60
BLOCK_SIZE = 110
BLOCK_MARGIN = 10
TITLE_HEIGHT = 110
ANIM_SLEEP_TIME = 25
STORE_FILE = 'store.json'

TITLE_COLOR = (243, 220, 202)
FIELD_COLOR = (187, 173, 160)

FIELD_COLORS = [dict()] * 2049
FIELD_COLORS[0] = dict(fg=(205, 193, 180), bg=(205, 193, 180))
FIELD_COLORS[2] = dict(fg=(119, 110, 98), bg=(238, 228, 218))
FIELD_COLORS[4] = dict(fg=(119, 110, 98), bg=(234, 222, 198))
FIELD_COLORS[8] = dict(fg=(249, 246, 242), bg=(242, 177, 121))
FIELD_COLORS[16] = dict(fg=(249, 246, 242), bg=(245, 149, 99))
FIELD_COLORS[32] = dict(fg=(249, 246, 242), bg=(246, 124, 95))
FIELD_COLORS[64] = dict(fg=(249, 246, 242), bg=(246, 94, 59))
FIELD_COLORS[128] = dict(fg=(249, 246, 242), bg=(237, 207, 114))
FIELD_COLORS[256] = dict(fg=(249, 246, 242), bg=(237, 204, 97))
FIELD_COLORS[512] = dict(fg=(249, 246, 242), bg=(237, 200, 80))
FIELD_COLORS[1024] = dict(fg=(249, 246, 242), bg=(237, 197, 63))
FIELD_COLORS[2048] = dict(fg=(249, 246, 242), bg=(237, 194, 46))


class Game2048:

    def __init__(self):
        self._array_size = 4
        # GUI
        pygame.display.set_caption('2048')
        pygame.init()
        self._best_score = 0
        self._width = self._array_size * BLOCK_SIZE + (self._array_size + 1) * BLOCK_MARGIN
        self._height = self._width + TITLE_HEIGHT
        self._clock = pygame.time.Clock()
        self._font = pygame.font.SysFont('', 72)
        # Surfaces
        self._screen = pygame.display.set_mode((self._width, self._height))
        self._menu = pygame.Surface((self._width, TITLE_HEIGHT))
        self._menu_rect = self._menu.get_rect()
        self._field = pygame.Surface((self._width, self._width))
        self._field_rect = self._field.get_rect(top=TITLE_HEIGHT)
        self._restart_button = self._create_button('(R)estart')
        self._restart_button_rect = self._restart_button.get_rect(topright=self._menu_rect.topright).move(-20, 15)
        self._quit_button = self._create_button('(Q)uit')
        self._quit_button_rect = self._quit_button.get_rect(bottomright=self._menu_rect.bottomright).move(-20, -15)

    def start(self, init_array=None):
        self.init(init_array)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        self.quit()
                    elif event.key == pygame.K_r:
                        self.restart(init_array)
                    elif event.key in [pygame.K_DOWN, pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT]:
                        self._move_array(event.key)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self._restart_button_rect.collidepoint(event.pos):
                        self.restart(init_array)
                    elif self._quit_button_rect.collidepoint(event.pos):
                        self.quit()

            self._draw_gui()
            self._clock.tick(FPS)

    def init(self, init_array=None):
        self._reset(init_array)

        try:
            with open(STORE_FILE) as file:
                state = json.load(file)
        except FileNotFoundError:
            pass
        else:
            self._best_score = state.get('best_score', 0)
            self._game_over = state.get('game_over', False)
            if not init_array:
                init_array = state.get('array')
                self._init_array(init_array)

        self._game_action(init_array is None)

    def restart(self, init_array=None):
        self._reset(init_array)
        self._game_action(True)

    def quit(self):
        # State saving
        state = dict(
            best_score=self._best_score,
            game_over=self._game_over,
            array=self._array
        )
        with open(STORE_FILE, 'w') as file:
            json.dump(state, file, indent=2)

        # Quit
        pygame.quit()
        sys.exit(0)

    def print_array(self):
        print('-' * 15)
        for row in self._array:
            print(row)
        print()

    def _reset(self, init_array=None):
        self._game_over = False
        self._score = 0
        self._init_array(init_array)

    def _init_array(self, init_array=None):
        self._is_rotated_array = False
        if init_array:
            self._array = init_array
            return

        self._array = []
        for row_index in range(self._array_size):
            row = []
            for cell_index in range(self._array_size):
                row.append(0)
            self._array.append(row)

    def _game_action(self, add_new_value: bool):
        if add_new_value:
            empty_cells = self._get_empty_cells()
            random.shuffle(empty_cells)
            cell = empty_cells.pop()
            value = self._add_2_or_4(cell)
            print(f'Filled: ({cell[0] + 1}, {cell[1] + 1}) value: {value}')
            self._game_over = not self._is_zero_in_array()

        self._calc_score()
        self.print_array()

    def _move_array(self, key: int):
        """
        Сдвигает элементы поля в одно из направлений.
        Если поле сдвигается влево или вправо, то массив поворачивается по часовой стрелке на 90 градусов.
        Столбцы становятся строками и работает алгоритм для сдвига вверх и вниз.
        :param key: клавиша вверх, вниз, влево или вправо
        """
        if self._game_over:
            return

        if key in [pygame.K_LEFT, pygame.K_RIGHT]:
            self._rotate_array()

        merged_cells = []
        array_was_changed = False
        for current_row_index in range(self._array_size - 1):
            for row_index in reversed(range(current_row_index + 1)):
                for cell_index in range(self._array_size):
                    if key in [pygame.K_DOWN, pygame.K_RIGHT]:
                        y_pos = self._array_size - row_index - 2
                        y_another_pos = y_pos + 1
                        x_pos = cell_index
                    elif key in [pygame.K_UP, pygame.K_LEFT]:
                        y_pos = row_index + 1
                        y_another_pos = y_pos - 1
                        x_pos = cell_index
                    else:
                        break

                    current_value = self._array[y_pos][x_pos]
                    another_value = self._array[y_another_pos][x_pos]

                    # Shifting and summing
                    if current_value != 0 and another_value == 0:
                        self._array[y_another_pos][x_pos] = self._array[y_pos][x_pos]
                        self._array[y_pos][x_pos] = 0
                        array_was_changed = True
                    elif x_pos not in merged_cells and current_value != 0 and current_value == another_value:
                        self._array[y_another_pos][x_pos] *= 2
                        self._array[y_pos][x_pos] = 0
                        merged_cells.append(x_pos)
                        array_was_changed = True

                if array_was_changed:
                    self._draw_gui()
                    pygame.time.wait(ANIM_SLEEP_TIME)

        if self._is_rotated_array:
            self._rotate_array()

        self._game_action(array_was_changed)

    def _draw_gui(self):
        self._screen.fill(TITLE_COLOR)

        # Menu drawing
        self._draw_menu()

        # Game field drawing
        self._draw_field()

        # Game over drawing
        if self._game_over:
            text = self._font.render('Game over', True, (0, 0, 0), (200, 200, 200))
            text_rect = text.get_rect(center=(self._width / 2, self._height / 2))
            self._screen.blit(text, text_rect)

        pygame.display.update()

    def _draw_menu(self):
        self._menu.fill(TITLE_COLOR)

        # Score drawing
        score_surface = self._create_info_block('SCORE', str(self._score))
        score_rect = score_surface.get_rect(topleft=(20, 15))
        self._menu.blit(score_surface, score_rect)

        # Best score drawing
        best_score_surface = self._create_info_block('BEST', str(self._best_score))
        best_score_rect = score_rect.move(score_rect.width + 20, 0)
        self._menu.blit(best_score_surface, best_score_rect)

        # Buttons drawing
        self._menu.blit(self._restart_button, self._restart_button_rect)
        self._menu.blit(self._quit_button, self._quit_button_rect)

        self._screen.blit(self._menu, self._menu_rect)

    @staticmethod
    def _create_info_block(text: str, value: str) -> Surface:
        surface = pygame.Surface((150, 80))
        surface.fill(FIELD_COLOR)

        # Text rendering
        font = pygame.font.SysFont('', 36)
        text_surface = font.render(text, True, (220, 220, 220))
        text_rect = text_surface.get_rect(midtop=surface.get_rect().midtop).move(0, 10)
        surface.blit(text_surface, text_rect)

        # Value rendering
        font = pygame.font.SysFont('', 55, bold=True)
        value_surface = font.render(value, True, (230, 230, 230))
        value_rect = value_surface.get_rect(midbottom=surface.get_rect().midbottom).move(0, -5)
        surface.blit(value_surface, value_rect)

        return surface

    @staticmethod
    def _create_button(text: str) -> Surface:
        surface = pygame.Surface((110, 35))
        surface.fill((143, 122, 102))
        font = pygame.font.SysFont('', 32)
        text_surface = font.render(text, True, (220, 220, 220))
        text_rect = text_surface.get_rect(center=surface.get_rect().center)
        surface.blit(text_surface, text_rect)
        return surface

    def _draw_field(self):
        array_was_rotated = False
        if self._is_rotated_array:
            self._rotate_array()
            array_was_rotated = True

        self._field.fill(FIELD_COLOR)
        for row_index in range(self._array_size):
            for cell_index in range(self._array_size):
                xcor = BLOCK_SIZE * cell_index + BLOCK_MARGIN * (cell_index + 1)
                ycor = BLOCK_SIZE * row_index + BLOCK_MARGIN * (row_index + 1)
                block = (xcor, ycor, BLOCK_SIZE, BLOCK_SIZE)
                value = self._array[row_index][cell_index]
                if value > len(FIELD_COLORS):
                    block_color = FIELD_COLORS[-1]
                else:
                    block_color = FIELD_COLORS[value]
                pygame.draw.rect(self._field, block_color['bg'], block)

                # Buttons text rendering
                font = pygame.font.SysFont('', self._get_value_font_size(value))
                text = font.render(str(value), True, block_color['fg'])
                text_rect = text.get_rect()
                text_rect.move_ip(
                    xcor + BLOCK_SIZE / 2 - text_rect.width / 2,
                    ycor + BLOCK_SIZE / 2 - text_rect.height / 2
                )
                self._field.blit(text, text_rect)

        self._screen.blit(self._field, self._field_rect)

        if array_was_rotated:
            self._rotate_array()

    @staticmethod
    def _get_value_font_size(value: int):
        if value >= 100000:
            return 40
        if value >= 10000:
            return 50
        if value >= 1000:
            return 60
        return 72

    def _calc_score(self):
        self._score = max([max(row) for row in self._array])
        self._best_score = max(self._best_score, self._score)

    def _is_zero_in_array(self):
        for row in self._array:
            for cell in row:
                if cell == 0:
                    return True
        return False

    def _get_empty_cells(self):
        empty_cells = []
        for row_index in range(self._array_size):
            for cell_index in range(self._array_size):
                if self._array[row_index][cell_index] == 0:
                    empty_cells.append((row_index, cell_index))
        return empty_cells

    def _add_2_or_4(self, cell: tuple[int, int]):
        x, y = cell
        self._array[x][y] = 2 if random.random() <= 0.75 else 4
        return self._array[x][y]

    def _rotate_array(self):
        """
        Если массив не был повернут то поворачивает его по часовой стрелке на 90 градусов.
        Иначе поворачивает его в исходное состояние.
        self._is_rotated_array - хранит состояние поворота массива
        """
        rotated_array = []

        for cell_index in range(self._array_size):
            row = []
            for row_index in range(self._array_size):
                row.append(self._array[row_index][cell_index])
            if not self._is_rotated_array:
                row.reverse()
            rotated_array.append(row)

        if self._is_rotated_array:
            rotated_array.reverse()

        self._array = rotated_array
        self._is_rotated_array = not self._is_rotated_array


if __name__ == '__main__':
    game = Game2048()
    game.start()
