from __future__ import annotations

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty
from kivy.clock import Clock

from board import Board
from controller import GameController, GameObserver, GameState


class CellButton(Button):
    """A single cell that remembers its board coordinates."""

    coords: tuple[int, int] | None = None


class TicTacToeLayout(BoxLayout):  # implements GameObserver structurally
    """Kivy UI layer for the Tic‑Tac‑Toe game."""

    # initial status so the label has something to render on the first frame
    status_message = StringProperty("X's turn")

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        # ------------------------------------------------------------------
        # model & controller
        # ------------------------------------------------------------------
        self._board = Board()
        self._controller = GameController(self._board)

        # ------------------------------------------------------------------
        # build grid of CellButtons
        # ------------------------------------------------------------------
        self._rows, self._cols = self._board.rows, self._board.cols
        self._cells: dict[tuple[int, int], CellButton] = {}

        self._grid = GridLayout(
            rows=self._rows,
            cols=self._cols,
            spacing=2,
            padding=2,
            size_hint=(1, 0.9),
        )

        for i in range(self._rows):
            for j in range(self._cols):
                btn = CellButton(font_size=32, disabled=self._board.is_obstacle(i, j))
                btn.coords = (i, j)
                btn.bind(on_release=self._on_cell_pressed)

                if self._board.is_obstacle(i, j):
                    btn.text = "#"
                    btn.background_color = (0.7, 0.7, 0.7, 1)

                self._cells[(i, j)] = btn
                self._grid.add_widget(btn)

        # ------------------------------------------------------------------
        # status label & restart button (hidden until round ends)
        # ------------------------------------------------------------------
        self._status_label = Label(text=self.status_message, size_hint=(1, 0.1))

        self._restart_btn = Button(
            text="Restart",
            size_hint=(1, 0.12),
            opacity=0,
            disabled=True,
        )
        self._restart_btn.bind(on_release=self._on_restart)

        # compose layout
        self.add_widget(self._grid)
        self.add_widget(self._status_label)
        self.add_widget(self._restart_btn)

        # ------------------------------------------------------------------
        # register *after* widgets exist, then paint first board
        # ------------------------------------------------------------------
        self._controller.register(self)
        self._refresh_board()

    # =====================================================================
    # UI  -> Controller
    # =====================================================================
    def _on_cell_pressed(self, btn: CellButton) -> None:
        if btn.coords is not None:
            self._controller.play(*btn.coords)

    # =====================================================================
    # GameObserver (Controller -> UI)  – methods required by the protocol
    # =====================================================================
    def on_board_change(self, coords, symbol) -> None:
        btn = self._cells[coords]
        btn.text = symbol
        btn.color = (1, 0, 0, 1) if symbol == "X" else (0, 0, 1, 1)
        btn.disabled = True

    def on_state_change(self, state: GameState, next_turn) -> None:
        if state is GameState.IN_PROGRESS:
            self.status_message = f"{next_turn}'s turn"
        elif state is GameState.DRAW:
            self.status_message = "Draw!"
            self._end_game()
        elif state is GameState.X_WON:
            self.status_message = "X wins!"
            self._end_game()
        elif state is GameState.O_WON:
            self.status_message = "O wins!"
            self._end_game()

        self._status_label.text = self.status_message

    # =====================================================================
    # helpers
    # =====================================================================
    def _end_game(self) -> None:
        """Disable all cells and reveal the Restart button."""
        for btn in self._cells.values():
            btn.disabled = True

        # fade‑in the restart button slightly later (smooth for Kivy)        
        Clock.schedule_once(
            lambda _dt: (
                setattr(self._restart_btn, "disabled", False),
                setattr(self._restart_btn, "opacity", 1),
            ),
            0.3,
        )

    def _on_restart(self, *_):
        """Callback for the Restart button – start a fresh round."""
        self._controller.reset()   # model reset + observer notification
        self._refresh_board()      # repaint view

        # hide the button again for the new round
        self._restart_btn.disabled = True
        self._restart_btn.opacity = 0

    def _refresh_board(self) -> None:
        """Synchronise each CellButton with the Board's current state."""
        for (i, j), btn in self._cells.items():
            if self._board.is_obstacle(i, j):
                btn.text = "#"
                btn.disabled = True
                btn.background_color = (0.7, 0.7, 0.7, 1)
            else:
                btn.text = ""
                btn.disabled = False
                btn.background_color = (1, 1, 1, 1)
                btn.color = (0, 0, 0, 1)

    # =====================================================================
    # Kivy app hook
    # =====================================================================


class TicTacToeApp(App):
    def build(self):
        return TicTacToeLayout()


if __name__ == "__main__":
    TicTacToeApp().run()
