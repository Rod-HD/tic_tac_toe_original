from __future__ import annotations

"""Kivy front‑end for 5×5 Tic‑Tac‑Toe (with obstacles).

Upgrades implemented in this revision
-------------------------------------
1. **UI components separated**  
   * `GameCell`  – a single button with row/col metadata.
   * `GameGrid`  – owns the GridLayout; provides `reset()` and
     `update_cell()` so the layout delegate (presenter) never touches
     internal widgets.
2. **Constructor‑based dependency injection**  
   * `TicTacToeLayout` receives an *already‑constructed* `GameController`.
   * A factory helper `create_game()` wires `Board → GameController → View`.
"""

from typing import Dict, Tuple

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.clock import Clock

from board import Board
from controller import GameController, GameObserver, GameState

# -----------------------------------------------------------------------------
# UI COMPONENTS (encapsulated)
# -----------------------------------------------------------------------------

class GameCell(Button):
    """Single grid cell that knows its own coordinates."""

    def __init__(self, row: int, col: int, **kw):
        super().__init__(**kw)
        self._row = row
        self._col = col

    # expose coordinates as read‑only properties
    @property
    def coords(self) -> Tuple[int, int]:
        return self._row, self._col


class GameGrid(GridLayout):
    """Widget that owns the full board of `GameCell`s.

    Public API intentionally small:
        * `reset(board: Board)`   – repaint whole board after model reset.
        * `update_cell(coords, symbol)` – paint an X/O and disable that cell.
    """

    def __init__(self, board: Board, on_cell_press, **kw):
        super().__init__(rows=board.rows, cols=board.cols, spacing=2, padding=2, **kw)
        self._cells: Dict[Tuple[int, int], GameCell] = {}
        self._build_cells(board, on_cell_press)

    # ------------------------------------------------------------------
    # public helpers
    # ------------------------------------------------------------------

    def reset(self, board: Board):
        for (i, j), cell in self._cells.items():
            if board.is_obstacle(i, j):
                self._paint_obstacle(cell)
            else:
                self._paint_blank(cell)

    def update_cell(self, coords: Tuple[int, int], symbol: str):
        cell = self._cells[coords]
        cell.text = symbol
        cell.color = (1, 0, 0, 1) if symbol == "X" else (0, 0, 1, 1)
        cell.disabled = True

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------

    def _build_cells(self, board: Board, on_press):
        for i in range(board.rows):
            for j in range(board.cols):
                cell = GameCell(i, j, font_size=32)
                cell.bind(on_release=on_press)
                self._cells[(i, j)] = cell
                self.add_widget(cell)
        self.reset(board)

    @staticmethod
    def _paint_obstacle(cell: Button):
        cell.text = "#"
        cell.disabled = True
        cell.background_color = (0.7, 0.7, 0.7, 1)

    @staticmethod
    def _paint_blank(cell: Button):
        cell.text = ""
        cell.disabled = False
        cell.background_color = (1, 1, 1, 1)
        cell.color = (0, 0, 0, 1)


# -----------------------------------------------------------------------------
# LAYOUT / PRESENTER (implements GameObserver)
# -----------------------------------------------------------------------------

class TicTacToeLayout(BoxLayout):
    """Presenter layer that receives a *ready* GameController via DI."""

    status_message = StringProperty("X's turn")

    def __init__(self, controller: GameController, **kw):
        super().__init__(orientation="vertical", **kw)
        self._controller = controller
        self._board = controller._board  # safe: controller guarantees board attribute

        # grid component -------------------------------------------------
        self._grid = GameGrid(self._board, self._on_cell_pressed, size_hint=(1, 0.9))

        # status + restart ----------------------------------------------
        self._status = Label(text=self.status_message, size_hint=(1, 0.1))
        self._restart = Button(text="Restart", size_hint=(1, 0.12), opacity=0, disabled=True)
        self._restart.bind(on_release=self._on_restart)

        # add widgets ----------------------------------------------------
        self.add_widget(self._grid)
        self.add_widget(self._status)
        self.add_widget(self._restart)

        # observe after widgets ready -----------------------------------
        self._controller.register(self)

    # ------------------------------------------------------------------
    # UI events → controller
    # ------------------------------------------------------------------

    def _on_cell_pressed(self, cell: GameCell):
        self._controller.play(*cell.coords)

    def _on_restart(self, *_):
        self._controller.reset()
        self._grid.reset(self._board)
        self._hide_restart()

    # ------------------------------------------------------------------
    # GameObserver callbacks
    # ------------------------------------------------------------------

    def on_board_change(self, coords, symbol):
        self._grid.update_cell(coords, symbol)

    def on_state_change(self, state: GameState, next_turn):
        if state is GameState.IN_PROGRESS:
            self.status_message = f"{next_turn}'s turn"
            self._hide_restart()
        else:
            self.status_message = ("Draw!" if state is GameState.DRAW else f"{state.name.split('_')[0]} wins!")
            self._end_game()
        self._status.text = self.status_message

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _end_game(self):
        Clock.schedule_once(lambda _dt: self._show_restart(), 0.3)

    def _show_restart(self):
        self._restart.disabled = False
        self._restart.opacity = 1

    def _hide_restart(self):
        self._restart.disabled = True
        self._restart.opacity = 0


# -----------------------------------------------------------------------------
# Dependency‑injection factory
# -----------------------------------------------------------------------------

def create_game() -> TicTacToeLayout:
    """Wire Board → GameController → View and return the ready UI root."""
    board = Board()
    controller = GameController(board)
    layout = TicTacToeLayout(controller)
    return layout


# -----------------------------------------------------------------------------
# Kivy App entry point
# -----------------------------------------------------------------------------

class TicTacToeApp(App):
    def build(self):
        return create_game()


if __name__ == "__main__":
    TicTacToeApp().run()
