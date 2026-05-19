from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from .board import AI, EMPTY, HUMAN, Board, Move, apply_move, board_size, get_status, iter_cells, undo_move

WIN_SCORE = 1_000_000
LOSE_SCORE = -1_000_000
FORK_CANDIDATE_LIMIT = 12

BoardKey = Tuple[Tuple[str, ...], ...]
CacheKey = Tuple[BoardKey, int, bool]
TranspositionTable = Dict[CacheKey, int]


@dataclass(frozen=True)
class SearchResult:
    move: Optional[Move]
    value: int
    depth: int
    nodes: int
    elapsed_ms: float
    algorithm: str


@dataclass
class SearchCounter:
    nodes: int = 0


def evaluate_board(board: Sequence[Sequence[str]]) -> int:
    status = get_status(board)
    if status.winner == AI:
        return WIN_SCORE
    if status.winner == HUMAN:
        return LOSE_SCORE
    if status.is_draw:
        return 0

    score = 0
    for line in _windows_of_four(board):
        score += _score_window(line)
    score += _score_sequences(board, AI)
    score -= _score_sequences(board, HUMAN)
    score += _fork_score(board, AI)
    score -= _fork_score(board, HUMAN)
    return score


def _windows_of_four(board: Sequence[Sequence[str]]) -> List[List[str]]:
    size = board_size(board)
    directions = ((0, 1), (1, 0), (1, 1), (1, -1))
    windows: List[List[str]] = []

    for row in range(size):
        for col in range(size):
            for dr, dc in directions:
                end_row = row + 3 * dr
                end_col = col + 3 * dc
                if 0 <= end_row < size and 0 <= end_col < size:
                    windows.append([board[row + step * dr][col + step * dc] for step in range(4)])
    return windows


def _score_window(window: Sequence[str]) -> int:
    ai_count = window.count(AI)
    human_count = window.count(HUMAN)
    empty_count = window.count(EMPTY)

    if ai_count and human_count:
        return 0
    if ai_count == 4:
        return WIN_SCORE
    if human_count == 4:
        return LOSE_SCORE

    ai_weights = {3: 5_000, 2: 400, 1: 25}
    human_weights = {3: 6_000, 2: 450, 1: 20}
    if ai_count > 0 and empty_count > 0:
        return ai_weights.get(ai_count, 0)
    if human_count > 0 and empty_count > 0:
        return -human_weights.get(human_count, 0)
    return 0


def _score_sequences(board: Sequence[Sequence[str]], player: str) -> int:
    size = board_size(board)
    directions = ((0, 1), (1, 0), (1, 1), (1, -1))
    score = 0

    for row in range(size):
        for col in range(size):
            if board[row][col] != player:
                continue

            for dr, dc in directions:
                prev_row = row - dr
                prev_col = col - dc
                if 0 <= prev_row < size and 0 <= prev_col < size and board[prev_row][prev_col] == player:
                    continue

                length = 0
                nr, nc = row, col
                while 0 <= nr < size and 0 <= nc < size and board[nr][nc] == player:
                    length += 1
                    nr += dr
                    nc += dc

                before_open = 0 <= prev_row < size and 0 <= prev_col < size and board[prev_row][prev_col] == EMPTY
                after_open = 0 <= nr < size and 0 <= nc < size and board[nr][nc] == EMPTY
                open_ends = int(before_open) + int(after_open)
                score += _score_sequence(length, open_ends, player)
    return score


def _score_sequence(length: int, open_ends: int, player: str) -> int:
    if open_ends == 0:
        return 0

    if length >= 4:
        return WIN_SCORE

    ai_weights = {
        (3, 2): 80_000,
        (3, 1): 18_000,
        (2, 2): 4_000,
        (2, 1): 900,
        (1, 2): 80,
        (1, 1): 20,
    }
    human_weights = {
        (3, 2): 95_000,
        (3, 1): 24_000,
        (2, 2): 4_800,
        (2, 1): 1_100,
        (1, 2): 70,
        (1, 1): 15,
    }
    weights = ai_weights if player == AI else human_weights
    return weights.get((length, open_ends), 0)


def _fork_score(board: Sequence[Sequence[str]], player: str) -> int:
    score = 0
    for move in generate_moves(board)[:FORK_CANDIDATE_LIMIT]:
        threats = _count_threats_after_move(board, move, player)
        if threats >= 2:
            score += 30_000 if player == AI else 38_000
    return score


def _count_threats_after_move(board: Sequence[Sequence[str]], move: Move, player: str) -> int:
    row, col = move
    size = board_size(board)
    directions = ((0, 1), (1, 0), (1, 1), (1, -1))
    threats = 0

    for dr, dc in directions:
        count = 1
        open_ends = 0
        for sign in (-1, 1):
            nr = row + sign * dr
            nc = col + sign * dc
            while 0 <= nr < size and 0 <= nc < size and board[nr][nc] == player:
                count += 1
                nr += sign * dr
                nc += sign * dc
            if 0 <= nr < size and 0 <= nc < size and board[nr][nc] == EMPTY:
                open_ends += 1

        if count >= 4 or (count == 3 and open_ends > 0) or (count == 2 and open_ends == 2):
            threats += 1
    return threats


def generate_moves(board: Sequence[Sequence[str]], radius: int = 1) -> List[Move]:
    size = board_size(board)
    occupied = [(row, col) for row, col in iter_cells(board) if board[row][col] != EMPTY]
    if not occupied:
        center = size // 2
        return [(center, center)]

    candidates = set()
    for row, col in occupied:
        for nr in range(max(0, row - radius), min(size, row + radius + 1)):
            for nc in range(max(0, col - radius), min(size, col + radius + 1)):
                if board[nr][nc] == EMPTY:
                    candidates.add((nr, nc))

    center = (size - 1) / 2
    return sorted(
        candidates,
        key=lambda move: (
            -_move_priority(board, move),
            abs(move[0] - center) + abs(move[1] - center),
            move[0],
            move[1],
        ),
    )


def _move_priority(board: Sequence[Sequence[str]], move: Move) -> int:
    row, col = move
    size = board_size(board)
    directions = ((0, 1), (1, 0), (1, 1), (1, -1))
    priority = 0

    for player, multiplier in ((AI, 3), (HUMAN, 4)):
        for dr, dc in directions:
            count = 1
            for sign in (-1, 1):
                nr = row + sign * dr
                nc = col + sign * dc
                while 0 <= nr < size and 0 <= nc < size and board[nr][nc] == player:
                    count += 1
                    nr += sign * dr
                    nc += sign * dc
            if count >= 4:
                priority += 100_000 * multiplier
            elif count == 3:
                priority += 5_000 * multiplier
            elif count == 2:
                priority += 300 * multiplier
    return priority


def choose_move(board: Board, depth: int, algorithm: str) -> SearchResult:
    normalized = algorithm.strip().lower()
    if normalized in {"minimax", "mm"}:
        return minimax_best_move(board, depth)
    if normalized in {"alphabeta", "alpha-beta", "ab"}:
        return alphabeta_best_move(board, depth)
    raise ValueError("Algorithm must be 'minimax' or 'alphabeta'")


def minimax_best_move(board: Board, depth: int) -> SearchResult:
    return _best_move(board, depth, "Minimax", _minimax)


def alphabeta_best_move(board: Board, depth: int) -> SearchResult:
    return _best_move(board, depth, "Alpha-Beta", _alphabeta)


def _best_move(
    board: Board,
    depth: int,
    algorithm_name: str,
    search_func: Callable[..., int],
) -> SearchResult:
    counter = SearchCounter()
    transposition: TranspositionTable = {}
    start = time.perf_counter()
    status = get_status(board)
    if status.is_finished:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return SearchResult(None, evaluate_board(board), depth, 1, elapsed_ms, algorithm_name)

    moves = generate_moves(board)

    if not moves:
        return SearchResult(None, evaluate_board(board), depth, 1, 0.0, algorithm_name)

    best_move: Optional[Move] = None
    best_value = -math.inf

    for move in moves:
        apply_move(board, move, AI)
        if algorithm_name == "Alpha-Beta":
            value = search_func(board, depth - 1, False, -math.inf, math.inf, counter, transposition)
        else:
            value = search_func(board, depth - 1, False, counter, transposition)
        undo_move(board, move)

        if value > best_value:
            best_value = value
            best_move = move

    elapsed_ms = (time.perf_counter() - start) * 1000
    return SearchResult(best_move, int(best_value), depth, counter.nodes, elapsed_ms, algorithm_name)


def _board_key(board: Sequence[Sequence[str]]) -> BoardKey:
    return tuple(tuple(row) for row in board)


def _minimax(
    board: Board,
    depth: int,
    is_maximizing: bool,
    counter: SearchCounter,
    transposition: TranspositionTable,
) -> int:
    counter.nodes += 1
    cache_key = (_board_key(board), depth, is_maximizing)
    cached = transposition.get(cache_key)
    if cached is not None:
        return cached

    status = get_status(board)
    if status.is_finished or depth == 0:
        value = evaluate_board(board)
        transposition[cache_key] = value
        return value

    moves = generate_moves(board)
    if is_maximizing:
        best_value = -math.inf
        for move in moves:
            apply_move(board, move, AI)
            best_value = max(best_value, _minimax(board, depth - 1, False, counter, transposition))
            undo_move(board, move)
        transposition[cache_key] = int(best_value)
        return int(best_value)

    best_value = math.inf
    for move in moves:
        apply_move(board, move, HUMAN)
        best_value = min(best_value, _minimax(board, depth - 1, True, counter, transposition))
        undo_move(board, move)
    transposition[cache_key] = int(best_value)
    return int(best_value)


def _alphabeta(
    board: Board,
    depth: int,
    is_maximizing: bool,
    alpha: float,
    beta: float,
    counter: SearchCounter,
    transposition: TranspositionTable,
) -> int:
    counter.nodes += 1
    cache_key = (_board_key(board), depth, is_maximizing)
    cached = transposition.get(cache_key)
    if cached is not None:
        return cached

    status = get_status(board)
    if status.is_finished or depth == 0:
        value = evaluate_board(board)
        transposition[cache_key] = value
        return value

    moves = generate_moves(board)
    if is_maximizing:
        value = -math.inf
        cut_off = False
        for move in moves:
            apply_move(board, move, AI)
            value = max(value, _alphabeta(board, depth - 1, False, alpha, beta, counter, transposition))
            undo_move(board, move)
            alpha = max(alpha, value)
            if beta <= alpha:
                cut_off = True
                break
        if not cut_off:
            transposition[cache_key] = int(value)
        return int(value)

    value = math.inf
    cut_off = False
    for move in moves:
        apply_move(board, move, HUMAN)
        value = min(value, _alphabeta(board, depth - 1, True, alpha, beta, counter, transposition))
        undo_move(board, move)
        beta = min(beta, value)
        if beta <= alpha:
            cut_off = True
            break
    if not cut_off:
        transposition[cache_key] = int(value)
    return int(value)
