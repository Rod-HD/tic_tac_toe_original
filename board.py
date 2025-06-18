import random
from typing import List, Tuple

class Board:
    """Game model: holds state and enforces the rules."""

    EMPTY, OBSTACLE = ".", "#"

    def __init__(
        self,
        rows: int = 5,
        cols: int = 5,
        win_len: int = 4,
        num_obstacles: int = 5,
    ) -> None:
        self._rows = rows
        self._cols = cols
        self._win_len = win_len
        self._num_obstacles = num_obstacles
        self.reset()

    # -------- public API --------------------------------------------------

    @property
    def rows(self) -> int: return self._rows

    @property
    def cols(self) -> int: return self._cols

    def reset(self) -> None:
        """Clear the board and randomly place fresh obstacles."""
        self._grid: List[List[str]] = [
            [self.EMPTY for _ in range(self._cols)] for _ in range(self._rows)
        ]
        self._place_obstacles()
        self._legal = {
            (i, j)
            for i in range(self._rows)
            for j in range(self._cols)
            if self._grid[i][j] == self.EMPTY
        }

    def is_empty(self, i: int, j: int) -> bool:
        return (i, j) in self._legal

    def is_obstacle(self, i: int, j: int) -> bool:
        return self._grid[i][j] == self.OBSTACLE

    def place(self, i: int, j: int, symbol: str) -> bool:
        """Attempt to place *symbol* at (i,j).  Return True on success."""
        if self.is_empty(i, j):
            self._grid[i][j] = symbol
            self._legal.remove((i, j))
            return True
        return False

    def is_full(self) -> bool:
        return not self._legal

    def has_winner(self, symbol: str) -> bool:
        """Check every direction for a win-len line of *symbol*."""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for i in range(self._rows):
            for j in range(self._cols):
                if self._grid[i][j] != symbol:
                    continue
                for di, dj in directions:
                    count, x, y = 1, i + di, j + dj
                    while (
                        0 <= x < self._rows
                        and 0 <= y < self._cols
                        and self._grid[x][y] == symbol
                    ):
                        count += 1
                        if count >= self._win_len:
                            return True
                        x += di
                        y += dj
        return False

    # -------- internal helpers --------------------------------------------

    def _place_obstacles(self) -> None:
        placed = 0
        while placed < self._num_obstacles:
            i = random.randrange(self._rows)
            j = random.randrange(self._cols)
            if self._grid[i][j] == self.EMPTY:
                self._grid[i][j] = self.OBSTACLE
                placed += 1
