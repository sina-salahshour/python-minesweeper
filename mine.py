import pygame
from enum import Enum, auto


class CellState(Enum):
    IDLE = auto()
    IDLE_SUNKEN = auto()
    FLAG = auto()
    QUESTION = auto()
    QUESTION_SUNKEN = auto()
    BOMB = auto()
    BOMB_WRONG = auto()
    BOMB_EXPLODED = auto()
    OPEN = auto()


class Win:
    pos = [0, 0]
    _zoom = 1
    _zoom_fr = 0.1
    _zoom_range = (0.5, 5)

    def __init__(self):
        self.stack = []

    def _add(self, item):
        self.stack.append(item)

    def _remove(self, item):
        self.stack.remove(item)

    def render(self, surface: pygame.Surface):
        win_pos_x, win_pos_y = self.pos
        for item in self.stack:
            (src_pos_x, src_pos_y), src = item.get_content()
            real_pos = [
                win_pos_x + src_pos_x * self._zoom,
                win_pos_y + src_pos_y * self._zoom,
            ]
            surface.blit(src, real_pos)

    def ch_zoom(self, fr_count, pos):
        zoom = self._zoom
        delta_zoom = self._zoom_fr * fr_count
        changed_zoom = zoom + delta_zoom
        self.pos[0] -= (pos[0] * changed_zoom) / zoom - pos[0]
        self.pos[1] -= (pos[1] * changed_zoom) / zoom - pos[1]
        if self._zoom_range[0] < changed_zoom < self._zoom_range[1]:
            self._zoom = changed_zoom

    @property
    def zoom(self):
        return self._zoom


class Cell:
    _idle_figure = pygame.image.load("assets/single-files/minesweeper_00.png")
    _idle_sunken_figure = _open_figure = pygame.image.load(
        "assets/single-files/minesweeper_01.png"
    )
    _flag_figure = pygame.image.load("assets/single-files/minesweeper_02.png")
    _question_figure = pygame.image.load("assets/single-files/minesweeper_03.png")
    _question_sunken_figure = pygame.image.load(
        "assets/single-files/minesweeper_04.png"
    )
    _bomb_figure = pygame.image.load("assets/single-files/minesweeper_05.png")
    _exploded_figure = pygame.image.load("assets/single-files/minesweeper_06.png")
    _bomb_wrong_figure = pygame.image.load("assets/single-files/minesweeper_07.png")
    _number_figures = [
        pygame.image.load(f"assets/single-files/minesweeper_{i:02d}.png")
        for i in range(8, 16)
    ]
    _fig_size = _idle_figure.get_size()[0]

    def __init__(self, win, field, grid, **kwargs) -> None:
        self.win = win
        self.state = kwargs.get("state", CellState.IDLE)
        self.origin = field.pos
        self.grid = grid
        self.pos = (
            self.origin[0] + self.grid[0] * self._fig_size,
            self.origin[1] + self.grid[1] * self._fig_size,
        )
        self.data = 0
        self.field = field
        win._add(self)

    def __del__(self):
        self.win._remove(self)

    def get_content(self):
        if self.state == CellState.IDLE:
            fig = self._idle_figure
        if self.state == CellState.IDLE_SUNKEN:
            fig = self._idle_sunken_figure
        if self.state == CellState.FLAG:
            fig = self._flag_figure
        if self.state == CellState.QUESTION:
            fig = self._question_figure
        if self.state == CellState.QUESTION_SUNKEN:
            fig = self._question_sunken_figure
        if self.state == CellState.OPEN:
            if self.data == 0:
                fig = self._open_figure
            else:
                fig = self._number_figures[self.data - 1]
        return (
            self.pos,
            pygame.transform.scale(fig, (self._fig_size * self.win.zoom,) * 2),
        )

    def click(self, btn):
        ...


class Field:
    def __init__(self, win, pos, grid):
        self.pos = pos
        self.win = win
        self.grid = grid
        self.cells = [
            [Cell(win, self, (i, j)) for i in range(grid[0])] for j in range(grid[1])
        ]
        self.cell_size = self.cells[0][0]._fig_size

    def mouse_over(self, pos):
        w_pos_x, w_pos_y = self.win.pos
        f_pos_x, f_pos_y = self.pos
        zoom = self.win.zoom
        return (
            w_pos_x + f_pos_x * zoom
            < pos[0]
            < w_pos_x + (f_pos_x + self.grid[0] * self.cell_size) * zoom
            and w_pos_y + f_pos_y * zoom
            < pos[1]
            < w_pos_y + (f_pos_y + self.grid[1] * self.cell_size) * zoom
        )

    def get_grid(self, pos):
        w_pos_x, w_pos_y = self.win.pos
        f_pos_x, f_pos_y = self.pos
        zoom = self.win.zoom
        x = int((((pos[0] - w_pos_x) / self.win.zoom) - f_pos_x) / self.cell_size)
        y = int((((pos[1] - w_pos_y) / self.win.zoom) - f_pos_y) / self.cell_size)
        return y, x

    def handle_mouse_click(self, pos, btn):
        if self.mouse_over(pos):
            self[self.get_grid(pos)].click(btn)

    def __getitem__(self, key):
        return self.cells[key[0]][key[1]]