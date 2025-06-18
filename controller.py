from enum import Enum, auto
from typing import List, Tuple, Protocol, Optional

from board import Board


class GameState(Enum):
    IN_PROGRESS = auto()
    X_WON = auto()
    O_WON = auto()
    DRAW = auto()


class GameObserver(Protocol):
    """Anything interested in board or state changes implements this."""

    def on_board_change(self, coords: Tuple[int, int], symbol: str) -> None: ...
    def on_state_change(
        self, state: GameState, next_turn: Optional[str]
    ) -> None: ...


class GameController:
    """Link between UI and model; enforces turn flow."""

    def __init__(self, board: Board) -> None:
        self._board = board
        self._current = "X"
        self._state = GameState.IN_PROGRESS
        self._observers: List[GameObserver] = []

    # -------- observer glue -----------------------------------------------

    def register(self, obs: GameObserver) -> None:
        self._observers.append(obs)
        # Immediately sync fresh observer with current state
        obs.on_state_change(self._state, self._current)

    def _notify_board(self, coords: Tuple[int, int]) -> None:
        for obs in self._observers:
            obs.on_board_change(coords, self._current)

    def _notify_state(self) -> None:
        nxt = None if self._state is not GameState.IN_PROGRESS else self._current
        for obs in self._observers:
            obs.on_state_change(self._state, nxt)

    # -------- public actions ----------------------------------------------

    def play(self, i: int, j: int) -> None:
        if self._state is not GameState.IN_PROGRESS:
            return
        if not self._board.place(i, j, self._current):
            return  # illegal move

        self._notify_board((i, j))

        if self._board.has_winner(self._current):
            self._state = (
                GameState.X_WON if self._current == "X" else GameState.O_WON
            )
        elif self._board.is_full():
            self._state = GameState.DRAW
        else:
            self._current = "O" if self._current == "X" else "X"

        self._notify_state()

    def reset(self) -> None:
        self._board.reset()
        self._current = "X"
        self._state = GameState.IN_PROGRESS
        self._notify_state()
