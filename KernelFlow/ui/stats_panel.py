"""
ui/stats_panel.py
=================
Right panel: statistics cards + ready queue display.

Shows all aggregate metrics as styled cards with color-coded values,
and a ready queue visualization updated by the main window.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List

from ui.theme import Colors, Fonts, Spacing


class StatsPanel(ttk.Frame):
    """
    Right-side panel displaying:
      - 6 metric stat cards (Avg WT, TAT, RT, CPU%, Throughput, Idle)
      - Ready queue visual strip
      - Algorithm info card
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, style="Card.TFrame", **kwargs)
        self._stat_labels: Dict[str, tk.Label] = {}
        self._build_ui()

    # ─────────────────────────────────────────────
    #  UI Construction
    # ─────────────────────────────────────────────

    def _build_ui(self):
        self.configure(padding=Spacing.CARD_PAD)

        # ── Header ────────────────────────────────
        tk.Label(
            self, text="📈  Statistics",
            bg=Colors.BG_SECONDARY, fg=Colors.ACCENT,
            font=Fonts.HEADING_3, anchor="w"
        ).pack(fill="x", pady=(0, Spacing.MD))

        # ── Stat Cards ────────────────────────────
        stats_config = [
            ("avg_waiting_time",    "Avg Waiting Time",     "—",   Colors.INFO),
            ("avg_turnaround_time", "Avg Turnaround Time",  "—",   Colors.ACCENT),
            ("avg_response_time",   "Avg Response Time",    "—",   Colors.WARNING),
            ("cpu_utilization",     "CPU Utilization",      "—",   Colors.SUCCESS),
            ("throughput",          "Throughput",           "—",   Colors.TEXT_PRIMARY),
            ("idle_time",           "Idle Time",            "—",   Colors.TEXT_SECONDARY),
        ]

        for key, label, default, color in stats_config:
            self._make_stat_card(key, label, default, color)

        # ── Divider ───────────────────────────────
        tk.Frame(self, bg=Colors.BORDER, height=1).pack(fill="x", pady=Spacing.MD)

        # ── Ready Queue Visualizer ─────────────────
        tk.Label(
            self, text="READY QUEUE",
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT_MUTED,
            font=(Fonts.FAMILY, Fonts.SIZE_XS, "bold"), anchor="w"
        ).pack(fill="x", pady=(0, Spacing.XS))

        self._queue_frame = tk.Frame(self, bg=Colors.BG_TERTIARY, height=40)
        self._queue_frame.pack(fill="x")
        self._queue_frame.pack_propagate(False)

        self._lbl_queue_empty = tk.Label(
            self._queue_frame, text="empty",
            bg=Colors.BG_TERTIARY, fg=Colors.TEXT_MUTED,
            font=Fonts.CAPTION
        )
        self._lbl_queue_empty.place(relx=0.5, rely=0.5, anchor="center")

        self._queue_chips: List[tk.Label] = []

        # ── Divider ───────────────────────────────
        tk.Frame(self, bg=Colors.BORDER, height=1).pack(fill="x", pady=Spacing.MD)

        # ── Algorithm Info Card ───────────────────
        tk.Label(
            self, text="ALGORITHM INFO",
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT_MUTED,
            font=(Fonts.FAMILY, Fonts.SIZE_XS, "bold"), anchor="w"
        ).pack(fill="x", pady=(0, Spacing.XS))

        info_card = tk.Frame(self, bg=Colors.BG_TERTIARY)
        info_card.pack(fill="x")

        self._lbl_algo_name = tk.Label(
            info_card, text="—",
            bg=Colors.BG_TERTIARY, fg=Colors.ACCENT,
            font=Fonts.LABEL_BOLD, anchor="w"
        )
        self._lbl_algo_name.pack(fill="x", padx=Spacing.SM, pady=(Spacing.SM, 0))

        self._lbl_algo_desc = tk.Label(
            info_card, text="Select an algorithm and run the simulation.",
            bg=Colors.BG_TERTIARY, fg=Colors.TEXT_SECONDARY,
            font=Fonts.CAPTION, anchor="w", wraplength=200, justify="left"
        )
        self._lbl_algo_desc.pack(fill="x", padx=Spacing.SM, pady=(0, Spacing.SM))

    def _make_stat_card(self, key: str, label: str, default: str, color: str):
        """Create a single metric card with value + label."""
        card = tk.Frame(self, bg=Colors.BG_TERTIARY)
        card.pack(fill="x", pady=Spacing.XS)

        # Value (large, colored)
        val_lbl = tk.Label(
            card, text=default,
            bg=Colors.BG_TERTIARY, fg=color,
            font=Fonts.STAT_VALUE, anchor="w"
        )
        val_lbl.pack(fill="x", padx=Spacing.SM, pady=(Spacing.SM, 0))
        self._stat_labels[key] = val_lbl

        # Label (small, muted)
        tk.Label(
            card, text=label,
            bg=Colors.BG_TERTIARY, fg=Colors.TEXT_MUTED,
            font=Fonts.STAT_LABEL, anchor="w"
        ).pack(fill="x", padx=Spacing.SM, pady=(0, Spacing.SM))

    # ─────────────────────────────────────────────
    #  Color Coding Logic
    # ─────────────────────────────────────────────

    def _color_for_cpu(self, value: float) -> str:
        """Green ≥80%, amber 50–79%, red <50%."""
        if value >= 80:
            return Colors.SUCCESS
        elif value >= 50:
            return Colors.WARNING
        return Colors.DANGER

    def _color_for_wait(self, value: float) -> str:
        """Low wait is good (green), high is bad (red)."""
        if value <= 3:
            return Colors.SUCCESS
        elif value <= 8:
            return Colors.WARNING
        return Colors.DANGER

    # ─────────────────────────────────────────────
    #  Public API
    # ─────────────────────────────────────────────

    def update_stats(self, metrics: Dict[str, Any], algorithm_name: str, description: str = ""):
        """Populate all stat cards from a metrics dict."""
        updates = {
            "avg_waiting_time":    (
                f"{metrics['avg_waiting_time']}",
                self._color_for_wait(metrics['avg_waiting_time'])
            ),
            "avg_turnaround_time": (
                f"{metrics['avg_turnaround_time']}",
                Colors.ACCENT
            ),
            "avg_response_time":   (
                f"{metrics['avg_response_time']}",
                Colors.WARNING
            ),
            "cpu_utilization":     (
                f"{metrics['cpu_utilization']}%",
                self._color_for_cpu(metrics['cpu_utilization'])
            ),
            "throughput":          (
                f"{metrics['throughput']}",
                Colors.TEXT_PRIMARY
            ),
            "idle_time":           (
                f"{metrics['idle_time']} units",
                Colors.TEXT_SECONDARY
            ),
        }
        for key, (text, color) in updates.items():
            lbl = self._stat_labels.get(key)
            if lbl:
                lbl.config(text=text, fg=color)

        self._lbl_algo_name.config(text=algorithm_name)
        self._lbl_algo_desc.config(
            text=description or "Simulation complete.",
            fg=Colors.TEXT_SECONDARY
        )

    def update_queue(self, queue_pids: List[str]):
        """Show the current ready queue as colored chips."""
        # Remove old chips
        for chip in self._queue_chips:
            chip.destroy()
        self._queue_chips.clear()

        if not queue_pids:
            self._lbl_queue_empty.place(relx=0.5, rely=0.5, anchor="center")
            return

        self._lbl_queue_empty.place_forget()

        for i, pid in enumerate(queue_pids):
            color = Colors.get_process_color(i)
            chip = tk.Label(
                self._queue_frame, text=f" {pid} ",
                bg=color, fg=Colors.BG_PRIMARY,
                font=Fonts.MONO_SM,
                relief="flat", padx=4, pady=2
            )
            chip.pack(side="left", padx=2, pady=4)
            self._queue_chips.append(chip)

    def clear_stats(self):
        """Reset all stat cards to their default state."""
        for lbl in self._stat_labels.values():
            lbl.config(text="—", fg=Colors.TEXT_MUTED)
        self.update_queue([])
        self._lbl_algo_name.config(text="—")
        self._lbl_algo_desc.config(
            text="Select an algorithm and run the simulation.",
            fg=Colors.TEXT_SECONDARY
        )
