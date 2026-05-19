from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Iterable, List

from .ai import alphabeta_best_move, minimax_best_move
from .board import Board, board_from_strings


def sample_states() -> Dict[str, Board]:
    return {
        "dau_van": board_from_strings(
            [
                ".........",
                ".........",
                ".........",
                ".........",
                ".........",
                ".........",
                ".........",
                ".........",
                ".........",
            ]
        ),
        "giua_van": board_from_strings(
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
        ),
        "may_thang_ngay": board_from_strings(
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
        ),
        "can_chan_nguoi": board_from_strings(
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
        ),
        "hai_ben_tan_cong": board_from_strings(
            [
                ".........",
                "...X.....",
                "...XO....",
                "....O....",
                "..OXX....",
                ".....O...",
                ".........",
                ".........",
                ".........",
            ]
        ),
        "nhieu_nhanh": board_from_strings(
            [
                ".........",
                "..X.O.X..",
                "...OXO...",
                ".XO...OX.",
                "..X.O.X..",
                ".O..X..O.",
                "...OXO...",
                "..O.X.O..",
                ".........",
            ]
        ),
    }


def run_benchmark(depths: Iterable[int] = (1, 2, 3)) -> List[dict]:
    rows: List[dict] = []
    for state_name, board in sample_states().items():
        for depth in depths:
            for search in (minimax_best_move, alphabeta_best_move):
                result = search([row[:] for row in board], depth)
                rows.append(
                    {
                        "state": state_name,
                        "algorithm": result.algorithm,
                        "depth": result.depth,
                        "move": "" if result.move is None else f"({result.move[0] + 1},{result.move[1] + 1})",
                        "value": result.value,
                        "states": result.nodes,
                        "time_ms": f"{result.elapsed_ms:.3f}",
                    }
                )
    return rows


def build_comparison_rows(rows: List[dict]) -> List[dict]:
    grouped: Dict[tuple[str, int], dict[str, dict]] = {}
    for row in rows:
        grouped.setdefault((row["state"], int(row["depth"])), {})[row["algorithm"]] = row

    comparison_rows: List[dict] = []
    for (state, depth), pair in grouped.items():
        minimax = pair.get("Minimax")
        alphabeta = pair.get("Alpha-Beta")
        if minimax is None or alphabeta is None:
            continue

        minimax_states = int(minimax["states"])
        alphabeta_states = int(alphabeta["states"])
        minimax_time = float(minimax["time_ms"])
        alphabeta_time = float(alphabeta["time_ms"])
        state_reduction = 0.0 if minimax_states == 0 else (1 - alphabeta_states / minimax_states) * 100
        time_ratio = 0.0 if minimax_time == 0 else alphabeta_time / minimax_time

        comparison_rows.append(
            {
                "state": state,
                "depth": depth,
                "same_move": "yes" if minimax["move"] == alphabeta["move"] else "no",
                "minimax_move": minimax["move"],
                "alphabeta_move": alphabeta["move"],
                "minimax_states": minimax_states,
                "alphabeta_states": alphabeta_states,
                "state_reduction_percent": f"{state_reduction:.2f}",
                "minimax_time_ms": f"{minimax_time:.3f}",
                "alphabeta_time_ms": f"{alphabeta_time:.3f}",
                "time_ratio": f"{time_ratio:.3f}",
            }
        )
    return comparison_rows


def write_csv(rows: List[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["state", "algorithm", "depth", "move", "value", "states", "time_ms"])
        writer.writeheader()
        writer.writerows(rows)


def write_comparison_csv(rows: List[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "state",
            "depth",
            "same_move",
            "minimax_move",
            "alphabeta_move",
            "minimax_states",
            "alphabeta_states",
            "state_reduction_percent",
            "minimax_time_ms",
            "alphabeta_time_ms",
            "time_ratio",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_markdown(rows: List[dict]) -> None:
    print("| Trang thai | Thuat toan | Do sau | Nuoc di | Gia tri | So trang thai | Thoi gian (ms) |")
    print("|---|---:|---:|---:|---:|---:|---:|")
    for row in rows:
        print(
            f"| {row['state']} | {row['algorithm']} | {row['depth']} | {row['move']} | "
            f"{row['value']} | {row['states']} | {row['time_ms']} |"
        )


def print_comparison_markdown(rows: List[dict]) -> None:
    print("\n| Trang thai | Do sau | Cung nuoc di | Minimax states | Alpha-Beta states | Giam states (%) | Ti le thoi gian AB/MM |")
    print("|---|---:|---:|---:|---:|---:|---:|")
    for row in rows:
        print(
            f"| {row['state']} | {row['depth']} | {row['same_move']} | "
            f"{row['minimax_states']} | {row['alphabeta_states']} | "
            f"{row['state_reduction_percent']} | {row['time_ratio']} |"
        )


def main() -> None:
    rows = run_benchmark()
    comparison_rows = build_comparison_rows(rows)
    out_path = Path(__file__).resolve().parents[2] / "benchmark_results.csv"
    comparison_path = Path(__file__).resolve().parents[2] / "benchmark_comparison.csv"
    write_csv(rows, out_path)
    write_comparison_csv(comparison_rows, comparison_path)
    print_markdown(rows)
    print_comparison_markdown(comparison_rows)
    print(f"\nDa ghi ket qua vao: {out_path}")
    print(f"Da ghi bang so sanh vao: {comparison_path}")


if __name__ == "__main__":
    main()
