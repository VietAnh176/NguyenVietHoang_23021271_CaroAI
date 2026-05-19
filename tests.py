from caro.ai import alphabeta_best_move, choose_move, evaluate_board, generate_moves, minimax_best_move
from caro.benchmark import build_comparison_rows, run_benchmark, sample_states
from caro.board import AI, HUMAN, board_from_strings, check_winner, create_board, get_status, is_valid_move


def test_check_winner_four_directions() -> None:
    assert check_winner(board_from_strings(["OOOO.....", ".........", ".........", ".........", ".........", ".........", ".........", ".........", "........."])) == AI
    assert check_winner(board_from_strings(["X........", "X........", "X........", "X........", ".........", ".........", ".........", ".........", "........."])) == HUMAN
    assert check_winner(board_from_strings(["O........", ".O.......", "..O......", "...O.....", ".........", ".........", ".........", ".........", "........."])) == AI
    assert check_winner(board_from_strings(["...X.....", "..X......", ".X.......", "X........", ".........", ".........", ".........", ".........", "........."])) == HUMAN


def test_invalid_occupied_move() -> None:
    board = create_board()
    board[4][4] = HUMAN
    assert not is_valid_move(board, (4, 4))
    assert is_valid_move(board, (4, 5))


def test_ai_wins_immediately() -> None:
    board = board_from_strings(
        [
            ".........",
            ".........",
            "..OOO....",
            "...XX....",
            "....X....",
            ".........",
            ".........",
            ".........",
            ".........",
        ]
    )
    result = alphabeta_best_move(board, 2)
    assert result.move in {(2, 1), (2, 5)}


def test_ai_blocks_human_three() -> None:
    board = board_from_strings(
        [
            ".........",
            ".........",
            "..XXXO...",
            "...O.....",
            "....O....",
            ".........",
            ".........",
            ".........",
            ".........",
        ]
    )
    result = alphabeta_best_move(board, 2)
    assert result.move == (2, 1)


def test_minimax_and_alphabeta_same_depth_same_move() -> None:
    board = board_from_strings(
        [
            ".........",
            ".........",
            "...X.....",
            "...XO....",
            "....OX...",
            ".....O...",
            ".........",
            ".........",
            ".........",
        ]
    )
    minimax = minimax_best_move([row[:] for row in board], 2)
    alphabeta = alphabeta_best_move([row[:] for row in board], 2)
    assert minimax.move == alphabeta.move
    assert minimax.value == alphabeta.value


def test_evaluation_prefers_ai_position() -> None:
    board = board_from_strings(
        [
            ".........",
            ".........",
            "..OO.....",
            ".........",
            ".........",
            ".........",
            ".........",
            ".........",
            ".........",
        ]
    )
    assert evaluate_board(board) > 0


def test_evaluation_values_open_three_more_than_blocked_three() -> None:
    open_three = board_from_strings(
        [
            ".........",
            ".........",
            "...OOO...",
            ".........",
            ".........",
            ".........",
            ".........",
            ".........",
            ".........",
        ]
    )
    blocked_three = board_from_strings(
        [
            ".........",
            ".........",
            "..XOOO...",
            ".........",
            ".........",
            ".........",
            ".........",
            ".........",
            ".........",
        ]
    )
    assert evaluate_board(open_three) > evaluate_board(blocked_three)


def test_full_board_without_four_is_draw() -> None:
    board = board_from_strings(["XOX", "OXO", "OXO"])
    status = get_status(board)
    assert status.is_finished
    assert status.is_draw
    assert status.winner is None


def test_choose_move_rejects_unknown_algorithm() -> None:
    board = create_board()
    try:
        choose_move(board, 1, "unknown")
    except ValueError as exc:
        assert "Algorithm" in str(exc)
    else:
        raise AssertionError("choose_move must reject unknown algorithms")


def test_benchmark_has_many_branch_state_and_comparison_rows() -> None:
    states = sample_states()
    assert "nhieu_nhanh" in states
    assert len(generate_moves(states["nhieu_nhanh"])) > len(generate_moves(states["dau_van"]))

    rows = run_benchmark(depths=(1,))
    comparisons = build_comparison_rows(rows)
    assert len(comparisons) == len(states)
    assert all("state_reduction_percent" in row for row in comparisons)


if __name__ == "__main__":
    tests = [
        test_check_winner_four_directions,
        test_invalid_occupied_move,
        test_ai_wins_immediately,
        test_ai_blocks_human_three,
        test_minimax_and_alphabeta_same_depth_same_move,
        test_evaluation_prefers_ai_position,
        test_evaluation_values_open_three_more_than_blocked_three,
        test_full_board_without_four_is_draw,
        test_choose_move_rejects_unknown_algorithm,
        test_benchmark_has_many_branch_state_and_comparison_rows,
    ]
    for test in tests:
        test()
    print(f"Passed {len(tests)} tests.")
