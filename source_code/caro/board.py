from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

EMPTY = "."
HUMAN = "X"
AI = "O"
BOARD_SIZE = 9
WIN_LENGTH = 4

Move = Tuple[int, int]
Board = List[List[str]]


@dataclass(frozen=True)
class GameStatus:
    winner: Optional[str]
    is_draw: bool
    is_finished: bool


def create_board(size: int = BOARD_SIZE) -> Board:
    return [[EMPTY for _ in range(size)] for _ in range(size)]


def clone_board(board: Sequence[Sequence[str]]) -> Board:
    return [list(row) for row in board]


def board_size(board: Sequence[Sequence[str]]) -> int:
    return len(board)


def is_valid_move(board: Sequence[Sequence[str]], move: Move) -> bool:
    row, col = move
    size = board_size(board)
    return 0 <= row < size and 0 <= col < size and board[row][col] == EMPTY


def apply_move(board: Board, move: Move, player: str) -> None:
    if not is_valid_move(board, move):
        raise ValueError(f"Invalid move: {move}")
    row, col = move
    board[row][col] = player


def undo_move(board: Board, move: Move) -> None:
    row, col = move
    board[row][col] = EMPTY


def board_is_full(board: Sequence[Sequence[str]]) -> bool:
    return all(cell != EMPTY for row in board for cell in row)


def iter_cells(board: Sequence[Sequence[str]]) -> Iterable[Move]:
    size = board_size(board)
    for row in range(size):
        for col in range(size):
            yield row, col


def check_winner(board: Sequence[Sequence[str]]) -> Optional[str]:
    size = board_size(board)
    directions = ((0, 1), (1, 0), (1, 1), (1, -1))

    for row in range(size):
        for col in range(size):
            player = board[row][col]
            if player == EMPTY:
                continue

            for dr, dc in directions:
                end_row = row + (WIN_LENGTH - 1) * dr
                end_col = col + (WIN_LENGTH - 1) * dc
                if not (0 <= end_row < size and 0 <= end_col < size):
                    continue

                if all(board[row + step * dr][col + step * dc] == player for step in range(WIN_LENGTH)):
                    return player
    return None


def get_status(board: Sequence[Sequence[str]]) -> GameStatus:
    winner = check_winner(board)
    if winner is not None:
        return GameStatus(winner=winner, is_draw=False, is_finished=True)
    if board_is_full(board):
        return GameStatus(winner=None, is_draw=True, is_finished=True)
    return GameStatus(winner=None, is_draw=False, is_finished=False)


def format_board(board: Sequence[Sequence[str]]) -> str:
    size = board_size(board)
    header = "    " + " ".join(f"{col + 1:2d}" for col in range(size))
    rows = [header]
    for row_index, row in enumerate(board):
        rows.append(f"{row_index + 1:2d}  " + " ".join(f"{cell:>2}" for cell in row))
    return "\n".join(rows)


def board_from_strings(rows: Sequence[str]) -> Board:
    board = [list(row.strip()) for row in rows]
    if not board:
        raise ValueError("Board must not be empty")
    size = len(board)
    if any(len(row) != size for row in board):
        raise ValueError("Board must be square")
    allowed = {EMPTY, HUMAN, AI}
    invalid = sorted({cell for row in board for cell in row if cell not in allowed})
    if invalid:
        raise ValueError(f"Invalid board symbols: {invalid}")
    return board

