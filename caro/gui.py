from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from .ai import SearchResult, choose_move, generate_moves
from .board import AI, EMPTY, HUMAN, Move, apply_move, create_board, get_status, is_valid_move, undo_move


class RoundedButton(tk.Canvas):
    def __init__(
        self,
        parent: tk.Widget,
        text: str,
        command,
        bg: str,
        fg: str,
        hover_bg: str,
        width: int = 116,
        height: int = 38,
    ) -> None:
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0, cursor="hand2")
        self.command = command
        self.text = text
        self.fill = bg
        self.hover_fill = hover_bg
        self.fg = fg
        self.width = width
        self.height = height
        self._draw(bg)
        self.bind("<Enter>", lambda _event: self._draw(self.hover_fill))
        self.bind("<Leave>", lambda _event: self._draw(self.fill))
        self.bind("<Button-1>", lambda _event: self.command())

    def _draw(self, fill: str) -> None:
        self.delete("all")
        self._rounded_rect(2, 2, self.width - 2, self.height - 2, 16, fill=fill, outline="")
        self.create_text(
            self.width / 2,
            self.height / 2,
            text=self.text,
            fill=self.fg,
            font=("Segoe UI Semibold", 10),
        )

    def _rounded_rect(self, x1: int, y1: int, x2: int, y2: int, radius: int, **kwargs) -> None:
        points = [
            x1 + radius,
            y1,
            x2 - radius,
            y1,
            x2,
            y1,
            x2,
            y1 + radius,
            x2,
            y2 - radius,
            x2,
            y2,
            x2 - radius,
            y2,
            x1 + radius,
            y2,
            x1,
            y2,
            x1,
            y2 - radius,
            x1,
            y1 + radius,
            x1,
            y1,
        ]
        self.create_polygon(points, smooth=True, splinesteps=20, **kwargs)


class CaroGUI:
    CANVAS_SIZE = 640
    BOARD_PADDING = 18
    FONT = "Segoe UI Variable"
    FALLBACK_FONT = "Segoe UI"

    PAGE_BG = "#05070d"
    CARD_BG = "#111827"
    SECTION_BG = "#172033"
    SECTION_ALT_BG = "#13251e"
    SECTION_WARN_BG = "#2a210f"
    SECTION_INFO_BG = "#1c1733"
    BOARD_BG = "#fafafa"
    CELL_BG = "#f6f7f9"
    GRID_COLOR = "#dfe4ea"
    HUMAN_COLOR = "#0b6f9e"
    AI_COLOR = "#f0141f"
    LAST_MOVE_COLOR = "#dbeafe"
    LAST_MOVE_OUTLINE = "#60a5fa"
    SUGGEST_COLOR = "#dff8e8"
    SUGGEST_OUTLINE = "#38b66a"

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Caro AI")
        self.root.resizable(False, False)
        self.root.configure(bg=self.PAGE_BG)

        self.algorithm_var = tk.StringVar(value="alphabeta")
        self.size_var = tk.IntVar(value=9)
        self.depth_var = tk.IntVar(value=3)
        self.status_var = tk.StringVar(value="Bạn đi trước")
        self.stats_var = tk.StringVar(value="Chưa có nước máy")
        self.turn_var = tk.StringVar(value="Lượt: Bạn")

        self.board = create_board(self.size_var.get())
        self.game_over = False
        self.last_move: Move | None = None
        self.suggested_move: Move | None = None
        self.move_number = 1
        self.history: list[tuple[Move, str]] = []

        self.canvas: tk.Canvas
        self.log: tk.Text
        self.compare_table: ttk.Treeview

        self._configure_style()
        self._build_layout()
        self._new_game()

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Treeview", rowheight=25, font=(self.FALLBACK_FONT, 9), borderwidth=0, background="#0f172a", foreground="#e5e7eb", fieldbackground="#0f172a")
        style.configure("Treeview.Heading", font=(self.FALLBACK_FONT, 9, "bold"), background="#263244", foreground="#f8fafc")

    def _build_layout(self) -> None:
        outer = tk.Frame(self.root, bg=self.PAGE_BG, padx=16, pady=16)
        outer.grid(row=0, column=0, sticky="nsew")

        top = self._card(outer, padx=16, pady=14)
        top.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))

        self._header(top, "Caro AI").grid(row=0, column=0, padx=(0, 18))
        self._label(top, "Thuật toán").grid(row=0, column=1, padx=(0, 8))
        self._radio(top, "Minimax", "minimax").grid(row=0, column=2, padx=(0, 6))
        self._radio(top, "Alpha-Beta", "alphabeta").grid(row=0, column=3, padx=(0, 16))

        self._label(top, "Độ sâu").grid(row=0, column=4, padx=(0, 8))
        tk.Spinbox(top, from_=1, to=4, width=4, textvariable=self.depth_var, font=("Segoe UI Semibold", 10), bg="#0f172a", fg="#f8fafc", buttonbackground="#334155", relief="flat").grid(row=0, column=5)

        self._label(top, "Cỡ bàn").grid(row=0, column=6, padx=(16, 8))
        tk.Spinbox(top, from_=9, to=15, width=4, textvariable=self.size_var, font=("Segoe UI Semibold", 10), bg="#0f172a", fg="#f8fafc", buttonbackground="#334155", relief="flat").grid(row=0, column=7)

        self._button(top, "Ván mới", "#2563eb", "#1d4ed8", "#ffffff", self._new_game).grid(row=0, column=8, padx=(18, 0))
        self._button(top, "Máy đi trước", "#facc15", "#eab308", "#111827", self._ai_first).grid(row=0, column=9, padx=(8, 0))
        self._button(top, "Đi lại", "#475569", "#334155", "#ffffff", self._undo_turn).grid(row=0, column=10, padx=(8, 0))
        self._button(top, "Gợi ý", "#16a34a", "#15803d", "#ffffff", self._suggest_human_move).grid(row=0, column=11, padx=(8, 0))
        self._button(top, "So sánh", "#7c3aed", "#6d28d9", "#ffffff", self._compare_algorithms).grid(row=0, column=12, padx=(8, 0))

        board_card = self._card(outer, padx=14, pady=14)
        board_card.grid(row=1, column=0, sticky="n")

        self.canvas = tk.Canvas(
            board_card,
            width=self.CANVAS_SIZE,
            height=self.CANVAS_SIZE,
            bg=self.BOARD_BG,
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0)
        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<Motion>", self._on_canvas_motion)
        self.canvas.bind("<Leave>", lambda _event: self.canvas.config(cursor=""))

        side = tk.Frame(outer, bg=self.PAGE_BG)
        side.grid(row=1, column=1, sticky="n", padx=(16, 0))

        status_card = self._section_card(side, self.SECTION_BG)
        status_card.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self._header(status_card, "Trạng thái", bg=self.SECTION_BG).grid(row=0, column=0, sticky="w")
        self._value(status_card, self.status_var, wraplength=370, bg=self.SECTION_BG, color="#f8fafc").grid(row=1, column=0, sticky="w", pady=(4, 5))
        self._value(status_card, self.turn_var, bg=self.SECTION_BG, color="#cbd5e1").grid(row=2, column=0, sticky="w")

        ai_card = self._section_card(side, self.SECTION_ALT_BG)
        ai_card.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        self._header(ai_card, "Lượt máy", bg=self.SECTION_ALT_BG).grid(row=0, column=0, sticky="w")
        self._value(ai_card, self.stats_var, wraplength=370, justify="left", bg=self.SECTION_ALT_BG, color="#ecfdf5").grid(row=1, column=0, sticky="w", pady=(4, 0))

        compare_card = self._section_card(side, self.SECTION_INFO_BG)
        compare_card.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self._header(compare_card, "So sánh thuật toán", bg=self.SECTION_INFO_BG).grid(row=0, column=0, sticky="w")
        columns = ("algorithm", "move", "value", "states", "time")
        self.compare_table = ttk.Treeview(compare_card, columns=columns, show="headings", height=3)
        headings = {
            "algorithm": "Thuật toán",
            "move": "Nước",
            "value": "Điểm",
            "states": "Nút",
            "time": "ms",
        }
        widths = {"algorithm": 92, "move": 58, "value": 70, "states": 70, "time": 60}
        for column in columns:
            self.compare_table.heading(column, text=headings[column])
            self.compare_table.column(column, width=widths[column], anchor="center", stretch=False)
        self.compare_table.grid(row=1, column=0, sticky="w", pady=(6, 0))

        history_card = self._section_card(side, self.SECTION_WARN_BG)
        history_card.grid(row=3, column=0, sticky="ew")
        self._header(history_card, "Lịch sử", bg=self.SECTION_WARN_BG).grid(row=0, column=0, sticky="w")
        self.log = tk.Text(
            history_card,
            width=50,
            height=17,
            wrap="word",
            state="disabled",
            bg="#0f172a",
            fg="#f8fafc",
            relief="flat",
            borderwidth=0,
            font=(self.FALLBACK_FONT, 9),
            padx=10,
            pady=8,
        )
        self.log.grid(row=1, column=0, pady=(6, 0))

    def _card(self, parent: tk.Widget, padx: int, pady: int) -> tk.Frame:
        return tk.Frame(parent, bg=self.CARD_BG, padx=padx, pady=pady, bd=2, relief="raised", highlightthickness=1, highlightbackground="#2b3548")

    def _section_card(self, parent: tk.Widget, bg: str) -> tk.Frame:
        return tk.Frame(parent, bg=bg, padx=14, pady=12, bd=2, relief="raised", highlightthickness=1, highlightbackground="#334155")

    def _label(self, parent: tk.Widget, text: str) -> tk.Label:
        return tk.Label(parent, text=text, bg=parent["bg"], fg="#cbd5e1", font=("Segoe UI Semibold", 10))

    def _header(self, parent: tk.Widget, text: str, bg: str | None = None) -> tk.Label:
        return tk.Label(parent, text=text, bg=bg or parent["bg"], fg="#f8fafc", font=("Segoe UI Semibold", 13))

    def _value(
        self,
        parent: tk.Widget,
        variable: tk.StringVar,
        wraplength: int | None = None,
        justify: str = "left",
        color: str = "#e5e7eb",
        bg: str | None = None,
    ) -> tk.Label:
        return tk.Label(parent, textvariable=variable, bg=bg or parent["bg"], fg=color, font=(self.FALLBACK_FONT, 10), wraplength=wraplength, justify=justify)

    def _radio(self, parent: tk.Widget, text: str, value: str) -> tk.Radiobutton:
        return tk.Radiobutton(
            parent,
            text=text,
            value=value,
            variable=self.algorithm_var,
            bg=parent["bg"],
            activebackground=parent["bg"],
            fg="#e5e7eb",
            activeforeground="#ffffff",
            selectcolor="#1e40af",
            indicatoron=False,
            relief="raised",
            bd=2,
            padx=12,
            pady=5,
            font=("Segoe UI Semibold", 10),
        )

    def _button(self, parent: tk.Widget, text: str, bg: str, hover_bg: str, fg: str, command) -> RoundedButton:
        return RoundedButton(parent, text=text, command=command, bg=bg, hover_bg=hover_bg, fg=fg)

    def _new_game(self) -> None:
        size = max(9, min(15, int(self.size_var.get())))
        self.size_var.set(size)
        self.board = create_board(size)
        self.game_over = False
        self.last_move = None
        self.suggested_move = None
        self.move_number = 1
        self.history = []
        self.status_var.set("Bạn đi trước")
        self.turn_var.set("Lượt: Bạn")
        self.stats_var.set("Chưa có nước máy")
        self._clear_log()
        self._clear_comparison()
        self._append_log("Bắt đầu ván mới.")
        self._draw_board()

    def _on_canvas_motion(self, event: tk.Event) -> None:
        move = self._event_to_move(event)
        if self.game_over or move is None or not is_valid_move(self.board, move):
            self.canvas.config(cursor="")
        else:
            self.canvas.config(cursor="hand2")

    def _on_canvas_click(self, event: tk.Event) -> None:
        if self.game_over:
            return
        move = self._event_to_move(event)
        if move is None:
            return
        self._human_move(*move)

    def _event_to_move(self, event: tk.Event) -> Move | None:
        size = len(self.board)
        cell = self._cell_size()
        start = self.BOARD_PADDING
        end = start + size * cell
        if not (start <= event.x < end and start <= event.y < end):
            return None

        row = int((event.y - start) // cell)
        col = int((event.x - start) // cell)
        if 0 <= row < size and 0 <= col < size:
            return row, col
        return None

    def _human_move(self, row: int, col: int) -> None:
        move = (row, col)
        if not is_valid_move(self.board, move):
            messagebox.showwarning("Nước đi không hợp lệ", "Ô này đã có quân hoặc nằm ngoài bàn cờ.")
            return

        self.suggested_move = None
        self._record_move(move, HUMAN)
        self._append_log(f"{self.move_number}. Bạn: ({row + 1}, {col + 1})")
        self._draw_board()
        if self._finish_if_needed():
            return
        self._ai_move()

    def _record_move(self, move: Move, player: str) -> None:
        apply_move(self.board, move, player)
        self.history.append((move, player))
        self.last_move = move

    def _ai_first(self) -> None:
        if self.game_over:
            return
        if any(cell != EMPTY for board_row in self.board for cell in board_row):
            messagebox.showinfo("Không thể đi trước", "Bấm Ván mới nếu muốn máy mở cờ.")
            return
        self._ai_move()

    def _ai_move(self) -> None:
        self.status_var.set("Máy đang tính...")
        self.turn_var.set("Lượt: Máy")
        self.root.update_idletasks()

        result = choose_move(self.board, int(self.depth_var.get()), self.algorithm_var.get())
        if result.move is None:
            self._finish_if_needed()
            return

        self._record_move(result.move, AI)
        row, col = result.move
        self.stats_var.set(self._format_result_stats(result))
        self._append_log(
            f"{self.move_number}. Máy: ({row + 1}, {col + 1}) | {result.algorithm} | "
            f"điểm={result.value} | nút={result.nodes} | {result.elapsed_ms:.2f} ms"
        )
        self.move_number = self._next_move_number()
        self.suggested_move = None
        self._draw_board()
        self._finish_if_needed()

    def _undo_turn(self) -> None:
        if not self.history:
            messagebox.showinfo("Đi lại", "Chưa có nước nào để đi lại.")
            return

        undone: list[tuple[Move, str]] = []
        move, player = self.history.pop()
        undo_move(self.board, move)
        undone.append((move, player))

        if player == AI and self.history and self.history[-1][1] == HUMAN:
            move, player = self.history.pop()
            undo_move(self.board, move)
            undone.append((move, player))

        self.game_over = False
        self.suggested_move = None
        self.last_move = self.history[-1][0] if self.history else None
        self.move_number = self._next_move_number()
        self.status_var.set("Đã quay lại lượt trước")
        self.turn_var.set("Lượt: Bạn")
        self.stats_var.set("Bạn có thể chọn nước khác.")
        self._clear_comparison()
        undone_text = ", ".join(f"{'Máy' if player == AI else 'Bạn'} {_format_move(move)}" for move, player in undone)
        self._append_log(f"Đi lại: {undone_text}")
        self._draw_board()

    def _next_move_number(self) -> int:
        return sum(1 for _move, player in self.history if player == AI) + 1

    def _suggest_human_move(self) -> None:
        if self.game_over:
            return

        self.status_var.set("Đang tìm gợi ý...")
        self.root.update_idletasks()

        move, score = self._best_human_hint()
        if move is None:
            messagebox.showinfo("Gợi ý", "Không còn nước đi hợp lệ.")
            return

        self.suggested_move = move
        self._draw_board()
        self.status_var.set(f"Gợi ý: ({move[0] + 1}, {move[1] + 1})")
        self.stats_var.set(f"Nước nên cân nhắc: ({move[0] + 1}, {move[1] + 1})\nĐiểm sau lượt phản hồi: {score}")
        self._append_log(f"Gợi ý: ({move[0] + 1}, {move[1] + 1}) | điểm={score}")

    def _best_human_hint(self) -> tuple[Move | None, int]:
        best_move: Move | None = None
        best_score = float("inf")
        depth = max(1, int(self.depth_var.get()) - 1)

        for move in generate_moves(self.board):
            apply_move(self.board, move, HUMAN)
            status = get_status(self.board)
            if status.winner == HUMAN:
                score = -1_000_000
            elif status.is_finished:
                score = 0
            else:
                reply = choose_move(self.board, depth, "alphabeta")
                score = reply.value
            undo_move(self.board, move)

            if score < best_score:
                best_score = score
                best_move = move

        return best_move, int(best_score) if best_move is not None else 0

    def _compare_algorithms(self) -> None:
        if self.game_over:
            return

        self.status_var.set("Đang so sánh...")
        self.root.update_idletasks()

        depth = int(self.depth_var.get())
        minimax = choose_move([row[:] for row in self.board], depth, "minimax")
        alphabeta = choose_move([row[:] for row in self.board], depth, "alphabeta")
        reduction = 0.0 if minimax.nodes == 0 else (1 - alphabeta.nodes / minimax.nodes) * 100
        time_ratio = 0.0 if minimax.elapsed_ms == 0 else alphabeta.elapsed_ms / minimax.elapsed_ms

        self._fill_comparison(minimax, alphabeta)
        self.stats_var.set(
            f"Cùng nước: {'có' if minimax.move == alphabeta.move else 'không'}\n"
            f"Giảm số trạng thái: {reduction:.2f}%\n"
            f"Tỉ lệ thời gian AB/MM: {time_ratio:.3f}"
        )
        self.status_var.set("Đã so sánh xong")
        self._append_log(
            "So sánh: "
            f"Minimax {_format_move(minimax.move)} nút={minimax.nodes}, "
            f"Alpha-Beta {_format_move(alphabeta.move)} nút={alphabeta.nodes}, "
            f"giảm={reduction:.2f}%"
        )

    def _finish_if_needed(self) -> bool:
        status = get_status(self.board)
        if not status.is_finished:
            self.status_var.set("Đến lượt bạn")
            self.turn_var.set("Lượt: Bạn")
            return False

        self.game_over = True
        if status.is_draw:
            message = "Kết quả: Hòa."
        elif status.winner == HUMAN:
            message = "Kết quả: Bạn thắng."
        else:
            message = "Kết quả: Máy thắng."
        self.status_var.set(message)
        self.turn_var.set("Ván cờ đã kết thúc")
        self._append_log(message)
        self._draw_board()
        messagebox.showinfo("Kết thúc ván cờ", message)
        return True

    def _draw_board(self) -> None:
        self.canvas.delete("all")
        size = len(self.board)

        self.canvas.create_rectangle(0, 0, self.CANVAS_SIZE, self.CANVAS_SIZE, fill=self.BOARD_BG, outline="")

        for row in range(size):
            for col in range(size):
                x1, y1, x2, y2 = self._cell_bounds(row, col)
                fill = self.CELL_BG
                outline = self.GRID_COLOR
                width = 1
                if self.suggested_move == (row, col) and is_valid_move(self.board, (row, col)):
                    fill = self.SUGGEST_COLOR
                    outline = self.SUGGEST_OUTLINE
                    width = 2
                elif self.last_move == (row, col):
                    fill = self.LAST_MOVE_COLOR
                    outline = self.LAST_MOVE_OUTLINE
                    width = 2
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=width)

        for row, board_row in enumerate(self.board):
            for col, cell_value in enumerate(board_row):
                if cell_value == HUMAN:
                    self._draw_x(row, col)
                elif cell_value == AI:
                    self._draw_o(row, col)

    def _draw_x(self, row: int, col: int) -> None:
        x, y = self._cell_center(row, col)
        half = self._cell_size() * 0.27
        self.canvas.create_line(x - half, y - half, x + half, y + half, fill=self.HUMAN_COLOR, width=7, capstyle="round")
        self.canvas.create_line(x + half, y - half, x - half, y + half, fill=self.HUMAN_COLOR, width=7, capstyle="round")

    def _draw_o(self, row: int, col: int) -> None:
        x, y = self._cell_center(row, col)
        radius = self._cell_size() * 0.26
        self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, outline=self.AI_COLOR, width=6)

    def _cell_size(self) -> float:
        size = len(self.board)
        return (self.CANVAS_SIZE - 2 * self.BOARD_PADDING) / size

    def _cell_bounds(self, row: int, col: int) -> tuple[float, float, float, float]:
        cell = self._cell_size()
        x1 = self.BOARD_PADDING + col * cell
        y1 = self.BOARD_PADDING + row * cell
        return x1, y1, x1 + cell, y1 + cell

    def _cell_center(self, row: int, col: int) -> tuple[float, float]:
        x1, y1, x2, y2 = self._cell_bounds(row, col)
        return (x1 + x2) / 2, (y1 + y2) / 2

    def _format_result_stats(self, result: SearchResult) -> str:
        return (
            f"{result.algorithm}\n"
            f"Nước đi: {_format_move(result.move)}\n"
            f"Điểm: {result.value}\n"
            f"Độ sâu: {result.depth}\n"
            f"Trạng thái đã xét: {result.nodes}\n"
            f"Thời gian: {result.elapsed_ms:.2f} ms"
        )

    def _fill_comparison(self, *results: SearchResult) -> None:
        self._clear_comparison()
        for result in results:
            self.compare_table.insert(
                "",
                "end",
                values=(
                    result.algorithm,
                    _format_move(result.move),
                    result.value,
                    result.nodes,
                    f"{result.elapsed_ms:.1f}",
                ),
            )

    def _clear_comparison(self) -> None:
        for item in self.compare_table.get_children():
            self.compare_table.delete(item)

    def _append_log(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _clear_log(self) -> None:
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")


def main() -> None:
    root = tk.Tk()
    CaroGUI(root)
    root.mainloop()


def _format_move(move: Move | None) -> str:
    if move is None:
        return "None"
    return f"({move[0] + 1}, {move[1] + 1})"


if __name__ == "__main__":
    main()
