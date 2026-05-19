from __future__ import annotations

from .ai import choose_move
from .board import AI, HUMAN, apply_move, create_board, format_board, get_status, is_valid_move


def ask_int(prompt: str, default: int) -> int:
    raw = input(prompt).strip()
    if not raw:
        return default
    return int(raw)


def ask_algorithm() -> str:
    raw = input("Chon AI (1 = Minimax, 2 = Alpha-Beta, 3 = So sanh, mac dinh 2): ").strip()
    if raw == "1":
        return "minimax"
    if raw == "3":
        return "compare"
    return "alphabeta"


def play() -> None:
    size = ask_int("Kich thuoc ban co (toi thieu 9, mac dinh 9): ", 9)
    size = max(9, size)
    depth = ask_int("Do sau tim kiem (mac dinh 3): ", 3)
    algorithm = ask_algorithm()
    board = create_board(size)

    print("\nNguoi choi: X | May: O")
    print("Nhap nuoc di theo dang: hang cot. Vi du: 5 5\n")

    while True:
        print(format_board(board))
        status = get_status(board)
        if status.is_finished:
            _print_result(status.winner, status.is_draw)
            return

        move = _read_human_move(board)
        apply_move(board, move, HUMAN)
        status = get_status(board)
        if status.is_finished:
            print(format_board(board))
            _print_result(status.winner, status.is_draw)
            return

        if algorithm == "compare":
            result = _compare_and_choose_move(board, depth)
        else:
            result = choose_move(board, depth, algorithm)
        if result.move is None:
            print("May khong con nuoc di hop le.")
            return
        apply_move(board, result.move, AI)

        row, col = result.move
        print(
            f"\nMay danh: ({row + 1}, {col + 1}) | "
            f"AI={result.algorithm} | value={result.value} | "
            f"depth={result.depth} | states={result.nodes} | "
            f"time={result.elapsed_ms:.2f} ms\n"
        )


def _compare_and_choose_move(board, depth: int):
    minimax = choose_move(board, depth, "minimax")
    alphabeta = choose_move(board, depth, "alphabeta")
    reduction = 0.0 if minimax.nodes == 0 else (1 - alphabeta.nodes / minimax.nodes) * 100
    time_ratio = 0.0 if minimax.elapsed_ms == 0 else alphabeta.elapsed_ms / minimax.elapsed_ms

    print("\nSo sanh hai thuat toan tren cung trang thai:")
    print(
        f"- Minimax: move={_format_move(minimax.move)}, value={minimax.value}, "
        f"states={minimax.nodes}, time={minimax.elapsed_ms:.2f} ms"
    )
    print(
        f"- Alpha-Beta: move={_format_move(alphabeta.move)}, value={alphabeta.value}, "
        f"states={alphabeta.nodes}, time={alphabeta.elapsed_ms:.2f} ms"
    )
    print(
        f"- Cung nuoc di: {'co' if minimax.move == alphabeta.move else 'khong'} | "
        f"giam states={reduction:.2f}% | ti le thoi gian AB/MM={time_ratio:.3f}\n"
    )
    return alphabeta


def _format_move(move) -> str:
    if move is None:
        return "None"
    return f"({move[0] + 1}, {move[1] + 1})"


def _read_human_move(board) -> tuple[int, int]:
    while True:
        raw = input("Nuoc di cua ban: ").strip()
        try:
            row_text, col_text = raw.split()
            move = (int(row_text) - 1, int(col_text) - 1)
        except ValueError:
            print("Nhap sai dinh dang. Hay nhap: hang cot")
            continue

        if is_valid_move(board, move):
            return move
        print("Nuoc di khong hop le hoac o da co quan.")


def _print_result(winner: str | None, is_draw: bool) -> None:
    if is_draw:
        print("Ket qua: Hoa.")
    elif winner == HUMAN:
        print("Ket qua: Ban thang.")
    else:
        print("Ket qua: May thang.")


if __name__ == "__main__":
    play()
