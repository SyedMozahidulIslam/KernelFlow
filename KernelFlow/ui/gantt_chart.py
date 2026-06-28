"""
ui/gantt_chart.py
=================
Matplotlib-powered Gantt chart embedded in Tkinter.

Features:
  - Horizontal colored bars per process execution block
  - Timeline axis with tick marks
  - Process labels on Y-axis
  - Color-matched to results table and stats panel
  - Step-by-step animation replay
  - Idle CPU gaps shown as hatched regions
  - Comparison bar chart across algorithms
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.ticker as ticker

from ui.theme import Colors, Fonts, Spacing


# Matplotlib dark style constants (mirroring ui/theme.py)
MPL = dict(
    fig_bg    = Colors.BG_PRIMARY,
    ax_bg     = "#13162A",
    text      = Colors.TEXT_PRIMARY,
    muted     = Colors.TEXT_MUTED,
    grid      = "#1E2235",
    border    = Colors.BORDER,
)


class GanttChart(ttk.Frame):
    """
    Embeds a Matplotlib Gantt chart inside a Tkinter frame.
    Renders process execution blocks as horizontal colored bars.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, style="Card.TFrame", **kwargs)
        self._gantt_blocks: List[dict] = []
        self._processes:    List       = []
        self._anim_index:   int        = 0
        self._anim_job:     Optional[str] = None
        self._build_ui()

    # ─────────────────────────────────────────────
    #  UI Construction
    # ─────────────────────────────────────────────

    def _build_ui(self):
        self.configure(padding=Spacing.CARD_PAD)

        # ── Header row ────────────────────────────
        hdr = tk.Frame(self, bg=Colors.BG_SECONDARY)
        hdr.pack(fill="x", pady=(0, Spacing.SM))

        tk.Label(
            hdr, text="📊  Gantt Chart",
            bg=Colors.BG_SECONDARY, fg=Colors.ACCENT,
            font=Fonts.HEADING_3, anchor="w"
        ).pack(side="left")

        # Animation controls
        ctrl = tk.Frame(hdr, bg=Colors.BG_SECONDARY)
        ctrl.pack(side="right")

        self._btn_replay = ttk.Button(
            ctrl, text="▶  Replay",
            style="TButton",
            command=self._start_animation
        )
        self._btn_replay.pack(side="left", padx=(0, Spacing.XS))

        self._btn_stop = ttk.Button(
            ctrl, text="⏹  Stop",
            style="TButton",
            command=self._stop_animation
        )
        self._btn_stop.pack(side="left")

        # ── Matplotlib Figure ─────────────────────
        self._fig = Figure(figsize=(8, 3.2), dpi=95)
        self._fig.patch.set_facecolor(MPL["fig_bg"])

        self._ax = self._fig.add_subplot(111)
        self._style_axes(self._ax)
        self._draw_placeholder()

        self._canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._canvas.get_tk_widget().pack(fill="both", expand=True)
        self._canvas.draw()

    # ─────────────────────────────────────────────
    #  Axes Styling
    # ─────────────────────────────────────────────

    def _style_axes(self, ax):
        """Apply dark theme to a matplotlib Axes object."""
        ax.set_facecolor(MPL["ax_bg"])
        ax.tick_params(colors=MPL["text"], labelsize=8)
        ax.xaxis.label.set_color(MPL["text"])
        ax.yaxis.label.set_color(MPL["text"])
        ax.title.set_color(MPL["text"])
        for spine in ax.spines.values():
            spine.set_edgecolor(MPL["border"])
        ax.grid(axis="x", color=MPL["grid"], linewidth=0.5, linestyle="--", alpha=0.7)

    def _draw_placeholder(self):
        """Show a friendly empty state before any simulation runs."""
        self._ax.clear()
        self._style_axes(self._ax)
        self._ax.text(
            0.5, 0.5,
            "Run a simulation to see the Gantt chart",
            ha="center", va="center",
            transform=self._ax.transAxes,
            color=MPL["muted"], fontsize=11,
            style="italic"
        )
        self._ax.set_xticks([])
        self._ax.set_yticks([])

    # ─────────────────────────────────────────────
    #  Core Render
    # ─────────────────────────────────────────────

    def render(self, gantt_blocks: List[dict], processes: list, algorithm_name: str = ""):
        """
        Draw the full Gantt chart.

        Args:
            gantt_blocks    : [{"pid": str, "start": int, "end": int}, ...]
            processes       : List of Process objects (for ordering Y-axis)
            algorithm_name  : Displayed in the chart title
        """
        self._gantt_blocks = gantt_blocks
        self._processes    = processes

        self._stop_animation()
        self._draw_gantt(gantt_blocks, processes, algorithm_name, up_to=len(gantt_blocks))

    def _draw_gantt(
        self,
        gantt_blocks: List[dict],
        processes:    list,
        algorithm_name: str,
        up_to:        int
    ):
        """Internal draw — renders only the first `up_to` blocks (for animation)."""
        self._ax.clear()
        self._style_axes(self._ax)

        if not gantt_blocks:
            self._draw_placeholder()
            self._canvas.draw()
            return

        # Build PID → color and PID → y-position maps
        pid_list  = list(dict.fromkeys(b["pid"] for b in gantt_blocks))  # ordered unique
        pid_color = {
            p.pid: Colors.get_process_color(i)
            for i, p in enumerate(processes)
        }
        pid_y = {pid: i for i, pid in enumerate(reversed(pid_list))}

        bar_height = 0.55
        max_time   = 0

        # ── Draw bars ─────────────────────────────
        visible_blocks = gantt_blocks[:up_to]

        for block in visible_blocks:
            pid   = block["pid"]
            start = block["start"]
            end   = block["end"]
            y     = pid_y.get(pid, 0)
            color = pid_color.get(pid, Colors.PROCESS_COLORS[0])
            width = end - start
            max_time = max(max_time, end)

            # Main bar
            rect = mpatches.FancyBboxPatch(
                (start, y - bar_height / 2),
                width, bar_height,
                boxstyle="round,pad=0.05",
                facecolor=color,
                edgecolor=Colors.BG_PRIMARY,
                linewidth=1.2,
                alpha=0.92,
                zorder=3
            )
            self._ax.add_patch(rect)

            # PID label inside the bar (only if wide enough)
            if width >= 1:
                self._ax.text(
                    start + width / 2, y,
                    pid,
                    ha="center", va="center",
                    fontsize=8, fontweight="bold",
                    color=Colors.BG_PRIMARY,
                    zorder=4
                )

            # Start-time label below bar
            self._ax.text(
                start, y - bar_height / 2 - 0.12,
                str(start),
                ha="center", va="top",
                fontsize=7, color=MPL["muted"],
                zorder=3
            )

        # End-time label for last visible block
        if visible_blocks:
            last = visible_blocks[-1]
            self._ax.text(
                last["end"], pid_y.get(last["pid"], 0) - bar_height / 2 - 0.12,
                str(last["end"]),
                ha="center", va="top",
                fontsize=7, color=MPL["muted"],
                zorder=3
            )

        # ── Idle gap detection & hatching ─────────
        all_times = sorted(set(
            t for b in visible_blocks for t in (b["start"], b["end"])
        ))
        if len(all_times) >= 2:
            for i in range(len(all_times) - 1):
                t_start = all_times[i]
                t_end   = all_times[i + 1]
                # Check if any block covers this gap
                covered = any(
                    b["start"] <= t_start and b["end"] >= t_end
                    for b in visible_blocks
                )
                if not covered:
                    # Draw idle stripe across all Y rows
                    for y in pid_y.values():
                        idle_rect = mpatches.Rectangle(
                            (t_start, y - bar_height / 2),
                            t_end - t_start, bar_height,
                            facecolor="none",
                            edgecolor=MPL["muted"],
                            linewidth=0.5,
                            linestyle="--",
                            alpha=0.4,
                            zorder=2
                        )
                        self._ax.add_patch(idle_rect)

        # ── Axes formatting ────────────────────────
        n_pids = len(pid_list)
        self._ax.set_xlim(-0.3, max_time + 0.8)
        self._ax.set_ylim(-0.7, n_pids - 0.3)
        self._ax.set_yticks(list(pid_y.values()))
        self._ax.set_yticklabels(list(reversed(pid_list)), fontsize=9, color=MPL["text"])

        # Integer x-ticks
        self._ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True, nbins=min(max_time, 20)))
        self._ax.set_xlabel("Time Units", color=MPL["muted"], fontsize=9)

        # Title
        title = f"Gantt Chart  —  {algorithm_name}" if algorithm_name else "Gantt Chart"
        self._ax.set_title(title, color=MPL["text"], fontsize=10, pad=8)

        # Legend
        legend_patches = []
        seen = set()
        for b in visible_blocks:
            if b["pid"] not in seen:
                seen.add(b["pid"])
                legend_patches.append(
                    mpatches.Patch(
                        facecolor=pid_color.get(b["pid"], "#999"),
                        label=b["pid"],
                        edgecolor=Colors.BG_PRIMARY,
                        linewidth=0.8
                    )
                )
        if legend_patches:
            self._ax.legend(
                handles=legend_patches,
                loc="upper right",
                fontsize=8,
                framealpha=0.2,
                facecolor=MPL["ax_bg"],
                edgecolor=MPL["border"],
                labelcolor=MPL["text"],
                ncol=min(len(legend_patches), 6)
            )

        self._fig.tight_layout(pad=1.2)
        self._canvas.draw()

    # ─────────────────────────────────────────────
    #  Step-by-Step Animation
    # ─────────────────────────────────────────────

    def _start_animation(self):
        """Replay the Gantt chart block by block."""
        if not self._gantt_blocks:
            return
        self._stop_animation()
        self._anim_index = 0
        self._animate_step()

    def _animate_step(self):
        """Draw one more block, then schedule the next step."""
        if self._anim_index > len(self._gantt_blocks):
            self._anim_job = None
            return

        algo = ""   # algorithm name not stored here; title is already set
        self._draw_gantt(
            self._gantt_blocks,
            self._processes,
            algo,
            up_to=self._anim_index
        )
        self._anim_index += 1
        # Schedule next step — 500ms per block
        self._anim_job = self.after(500, self._animate_step)

    def _stop_animation(self):
        """Cancel any running animation."""
        if self._anim_job is not None:
            self.after_cancel(self._anim_job)
            self._anim_job = None

    # ─────────────────────────────────────────────
    #  Comparison Chart
    # ─────────────────────────────────────────────

    def render_comparison(self, comparison_data: Dict[str, Dict]):
        """
        Draw a grouped bar chart comparing algorithms.

        Args:
            comparison_data : {algorithm_name: metrics_dict, ...}
        """
        self._stop_animation()
        self._ax.clear()
        self._style_axes(self._ax)

        if not comparison_data:
            self._draw_placeholder()
            self._canvas.draw()
            return

        algo_names = list(comparison_data.keys())
        avg_wt  = [comparison_data[a]["avg_waiting_time"]    for a in algo_names]
        avg_tat = [comparison_data[a]["avg_turnaround_time"] for a in algo_names]
        avg_rt  = [comparison_data[a]["avg_response_time"]   for a in algo_names]

        import numpy as np
        x      = np.arange(len(algo_names))
        width  = 0.25

        bar1 = self._ax.bar(x - width, avg_wt,  width, label="Avg WT",  color=Colors.INFO,    alpha=0.85, zorder=3)
        bar2 = self._ax.bar(x,         avg_tat, width, label="Avg TAT", color=Colors.ACCENT,  alpha=0.85, zorder=3)
        bar3 = self._ax.bar(x + width, avg_rt,  width, label="Avg RT",  color=Colors.WARNING, alpha=0.85, zorder=3)

        # Value labels on top of bars
        for bars in [bar1, bar2, bar3]:
            for bar in bars:
                h = bar.get_height()
                self._ax.text(
                    bar.get_x() + bar.get_width() / 2, h + 0.1,
                    f"{h:.1f}",
                    ha="center", va="bottom",
                    fontsize=7, color=MPL["text"]
                )

        self._ax.set_xticks(x)
        # Shorten long names for display
        short_names = [n.replace(" (Preemptive)", "\n(Pre)") for n in algo_names]
        self._ax.set_xticklabels(short_names, fontsize=8, color=MPL["text"])
        self._ax.set_ylabel("Time Units", color=MPL["muted"], fontsize=9)
        self._ax.set_title(
            "Algorithm Comparison  —  Avg Waiting / Turnaround / Response Time",
            color=MPL["text"], fontsize=10, pad=8
        )
        self._ax.legend(
            fontsize=8, framealpha=0.2,
            facecolor=MPL["ax_bg"],
            edgecolor=MPL["border"],
            labelcolor=MPL["text"]
        )

        self._fig.tight_layout(pad=1.2)
        self._canvas.draw()

    def clear(self):
        """Reset to placeholder state."""
        self._stop_animation()
        self._gantt_blocks = []
        self._processes    = []
        self._draw_placeholder()
        self._canvas.draw()
