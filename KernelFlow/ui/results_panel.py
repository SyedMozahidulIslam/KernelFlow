"""
ui/results_panel.py
===================
Center panel: two Treeview tables.
  1. Process Input Table  — shows the process list as entered
  2. Results Table        — shows computed CT, WT, TAT, RT after simulation
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional

from models.process import Process
from ui.theme import Colors, Fonts, Spacing


class ResultsPanel(ttk.Frame):
    """
    Displays process input data and simulation results in two styled tables.
    Row colors match the Gantt chart process colors for visual consistency.
    """

    # Table column definitions: (id, heading, width, anchor)
    INPUT_COLUMNS = [
        ("pid",      "PID",          70,  "center"),
        ("arrival",  "Arrival",      70,  "center"),
        ("burst",    "Burst",        70,  "center"),
        ("priority", "Priority",     70,  "center"),
    ]

    RESULT_COLUMNS = [
        ("pid",      "PID",          60,  "center"),
        ("arrival",  "Arrival",      60,  "center"),
        ("burst",    "Burst",        60,  "center"),
        ("ct",       "Completion",   85,  "center"),
        ("wt",       "Waiting",      75,  "center"),
        ("tat",      "Turnaround",   85,  "center"),
        ("rt",       "Response",     75,  "center"),
    ]

    def __init__(self, parent, **kwargs):
        super().__init__(parent, style="Card.TFrame", **kwargs)
        self._processes: List[Process] = []
        self._build_ui()

    # ─────────────────────────────────────────────
    #  UI Construction
    # ─────────────────────────────────────────────

    def _build_ui(self):
        self.configure(padding=Spacing.CARD_PAD)

        # ── Process Input Table ───────────────────
        lbl_input = tk.Label(
            self, text="📋  Process Queue",
            bg=Colors.BG_SECONDARY, fg=Colors.ACCENT,
            font=Fonts.HEADING_3, anchor="w"
        )
        lbl_input.pack(fill="x", pady=(0, Spacing.XS))

        self._input_tree = self._make_table(self, self.INPUT_COLUMNS, height=6)
        self._input_tree.pack(fill="x", pady=(0, Spacing.MD))

        # ── Divider ───────────────────────────────
        tk.Frame(self, bg=Colors.BORDER, height=1).pack(fill="x", pady=Spacing.SM)

        # ── Results Table ─────────────────────────
        lbl_results = tk.Label(
            self, text="📊  Simulation Results",
            bg=Colors.BG_SECONDARY, fg=Colors.ACCENT,
            font=Fonts.HEADING_3, anchor="w"
        )
        lbl_results.pack(fill="x", pady=(Spacing.SM, Spacing.XS))

        self._algo_label = tk.Label(
            self, text="No simulation run yet.",
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT_MUTED,
            font=Fonts.CAPTION, anchor="w"
        )
        self._algo_label.pack(fill="x", pady=(0, Spacing.XS))

        results_frame = tk.Frame(self, bg=Colors.BG_SECONDARY)
        results_frame.pack(fill="both", expand=True)

        self._result_tree = self._make_table(results_frame, self.RESULT_COLUMNS, height=8)

        # Scrollbar
        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self._result_tree.yview)
        self._result_tree.configure(yscrollcommand=vsb.set)
        self._result_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    def _make_table(self, parent, columns, height=6) -> ttk.Treeview:
        """Build and return a styled Treeview table."""
        col_ids = [c[0] for c in columns]
        tree = ttk.Treeview(
            parent,
            columns=col_ids,
            show="headings",
            height=height,
            style="Treeview",
        )
        for col_id, heading, width, anchor in columns:
            tree.heading(col_id, text=heading, anchor=anchor)
            tree.column(col_id,  width=width,  anchor=anchor, minwidth=50, stretch=True)

        return tree

    # ─────────────────────────────────────────────
    #  Public API
    # ─────────────────────────────────────────────

    def update_process_list(self, processes: List[Process]):
        """Refresh the input table when the process list changes."""
        self._processes = processes
        # Clear existing rows
        for row in self._input_tree.get_children():
            self._input_tree.delete(row)

        for idx, p in enumerate(processes):
            color = Colors.get_process_color(idx)
            tag   = f"proc_{idx}"
            self._input_tree.tag_configure(tag, foreground=color)
            self._input_tree.insert(
                "", "end",
                values=(p.pid, p.arrival_time, p.burst_time, p.priority),
                tags=(tag,)
            )

    def update_results(self, processes: List[Process], algorithm_name: str):
        """Populate the results table after a simulation run."""
        # Clear existing rows
        for row in self._result_tree.get_children():
            self._result_tree.delete(row)

        self._algo_label.config(
            text=f"Algorithm: {algorithm_name}",
            fg=Colors.ACCENT
        )

        # Build a PID→color map from the original process order
        pid_color = {
            p.pid: Colors.get_process_color(i)
            for i, p in enumerate(self._processes)
        }

        for p in processes:
            color = pid_color.get(p.pid, Colors.TEXT_PRIMARY)
            tag   = f"result_{p.pid}"
            self._result_tree.tag_configure(tag, foreground=color)

            row = p.to_table_row()
            # to_table_row returns (pid, arrival, burst, priority, ct, wt, tat, rt)
            # Reorder to match result columns: pid, arrival, burst, ct, wt, tat, rt
            display = (row[0], row[1], row[2], row[4], row[5], row[6], row[7])
            self._result_tree.insert("", "end", values=display, tags=(tag,))

    def clear_results(self):
        """Clear only the results table, keep the process input table."""
        for row in self._result_tree.get_children():
            self._result_tree.delete(row)
        self._algo_label.config(
            text="No simulation run yet.",
            fg=Colors.TEXT_MUTED
        )
