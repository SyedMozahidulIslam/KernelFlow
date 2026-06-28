"""
ui/main_window.py
=================
Root application window. Owns the layout and wires all panels together.

Layout (3-column):
  ┌──────────────┬────────────────────────┬──────────────┐
  │  InputPanel  │     ResultsPanel       │  StatsPanel  │
  │  (left)      │  + Notebook tabs:      │  (right)     │
  │              │    Gantt / Compare     │              │
  └──────────────┴────────────────────────┴──────────────┘

Communication flow:
  InputPanel ──[callbacks]──► MainWindow ──► ResultsPanel
                                         ──► StatsPanel
                                         ──► GanttChart
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional

from ui.theme      import Colors, Fonts, Spacing, apply_theme
from ui.input_panel   import InputPanel
from ui.results_panel import ResultsPanel
from ui.stats_panel   import StatsPanel
from ui.gantt_chart   import GanttChart
from utils.scheduler  import run_simulation, run_comparison, get_display_name, ALGORITHM_NAMES
from algorithms       import FCFS, SJF, RoundRobin, Priority
from models.process   import Process


# Algorithm description lookup for the stats panel info card
ALGO_DESCRIPTIONS = {
    "FCFS":                  "Non-preemptive. Processes execute in arrival order. Simple but suffers from convoy effect.",
    "SJF":                   "Non-preemptive. Selects the shortest burst job at each decision point. Optimal average WT.",
    "SJF (Preemptive)":      "SRTF — preempts the running process if a shorter job arrives. Minimum possible avg WT.",
    "Round Robin":           "Preemptive. Each process gets a fixed time quantum. Fair CPU sharing for interactive systems.",
    "Priority":              "Non-preemptive. Runs the highest-priority available process. Lower number = higher priority.",
    "Priority (Preemptive)": "Preemptive priority. Immediately preempts if a higher-priority process arrives.",
}


class MainWindow:
    """
    Root application controller.
    Creates the Tk window, applies the theme, builds the layout,
    and coordinates all panel interactions via callbacks.
    """

    APP_TITLE  = "KernelFlow  —  CPU Scheduling Simulator by SMI Fahim"
    MIN_WIDTH  = 1100
    MIN_HEIGHT = 700

    def __init__(self, root: tk.Tk):
        self.root = root
        self._setup_window()
        self._style = apply_theme(root)
        self._build_layout()


    def _setup_window(self):
        self.root.title(self.APP_TITLE)
        self.root.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.root.configure(bg=Colors.BG_PRIMARY)

        # Center on screen
        self.root.update_idletasks()
        w = max(self.MIN_WIDTH, self.root.winfo_screenwidth()  // 10 * 8)
        h = max(self.MIN_HEIGHT, self.root.winfo_screenheight() // 10 * 8)
        x = (self.root.winfo_screenwidth()  - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ─────────────────────────────────────────────
    #  Layout Construction
    # ─────────────────────────────────────────────

    def _build_layout(self):
        """Build the full 3-column application layout."""

        # ── App Header Bar ────────────────────────
        self._build_header()

        # ── Main Content Area ─────────────────────
        content = tk.Frame(self.root, bg=Colors.BG_PRIMARY)
        content.pack(fill="both", expand=True, padx=Spacing.MD, pady=(0, Spacing.MD))

        # PanedWindow for resizable columns
        paned = ttk.PanedWindow(content, orient="horizontal")
        paned.pack(fill="both", expand=True)

        # ── Left: Input Panel ─────────────────────
        self._input_panel = InputPanel(
            paned,
            on_run                   = self._on_run,
            on_reset                 = self._on_reset,
            on_process_list_changed  = self._on_process_list_changed,
        )
        paned.add(self._input_panel, weight=1)

        # ── Center: Results + Notebook tabs ───────
        center = ttk.Frame(paned, style="TFrame")
        paned.add(center, weight=3)

        self._results_panel = ResultsPanel(center)
        self._results_panel.pack(fill="both", expand=False, pady=(0, Spacing.XS))

        # Notebook for Gantt / Comparison tabs
        self._notebook = ttk.Notebook(center)
        self._notebook.pack(fill="both", expand=True)

        # Gantt tab
        gantt_frame = ttk.Frame(self._notebook, style="Card.TFrame")
        self._notebook.add(gantt_frame, text="  📊 Gantt Chart  ")
        self._gantt = GanttChart(gantt_frame)
        self._gantt.pack(fill="both", expand=True)

        # Comparison tab
        compare_frame = ttk.Frame(self._notebook, style="Card.TFrame")
        self._notebook.add(compare_frame, text="  ⚖  Compare All  ")
        self._build_compare_tab(compare_frame)

        # ── Right: Stats Panel ────────────────────
        self._stats_panel = StatsPanel(paned)
        paned.add(self._stats_panel, weight=1)

        # ── Status Bar ────────────────────────────
        self._build_statusbar()

    def _build_header(self):
        """Top header bar with app title and subtitle."""
        header = tk.Frame(self.root, bg=Colors.BG_SECONDARY, height=64)
        header.pack(fill="x")
        header.pack_propagate(False)

        inner = tk.Frame(header, bg=Colors.BG_SECONDARY)
        inner.place(relx=0.5, rely=0.5, anchor="center")

        # App icon + title
        tk.Label(
            inner, text="⚡ KernelFlow",
            bg=Colors.BG_SECONDARY, fg=Colors.ACCENT,
            font=Fonts.HEADING_2
        ).pack(side="left")

        tk.Label(
            inner, text="  A Simulator by SMI Fahim",
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT_SECONDARY,
            font=Fonts.LABEL
        ).pack(side="left")

        tk.Frame(self.root, bg=Colors.ACCENT, height=2).pack(fill="x")

    def _build_compare_tab(self, parent):
        """Build the algorithm comparison tab content."""
        ctrl = tk.Frame(parent, bg=Colors.BG_SECONDARY)
        ctrl.pack(fill="x", padx=Spacing.CARD_PAD, pady=Spacing.SM)

        tk.Label(
            ctrl,
            text="Compare all algorithms on the current process set.",
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT_SECONDARY,
            font=Fonts.CAPTION
        ).pack(side="left")

        # Quantum input for Round Robin in comparison
        tk.Label(
            ctrl, text="RR Quantum:",
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT_SECONDARY,
            font=Fonts.CAPTION
        ).pack(side="left", padx=(Spacing.LG, Spacing.XS))

        self._var_compare_quantum = tk.StringVar(value="2")
        tk.Entry(
            ctrl,
            textvariable=self._var_compare_quantum,
            bg=Colors.BG_TERTIARY, fg=Colors.TEXT_PRIMARY,
            font=Fonts.CAPTION, width=4,
            relief="flat", insertbackground=Colors.ACCENT,
            highlightthickness=1,
            highlightcolor=Colors.ACCENT,
            highlightbackground=Colors.BORDER,
        ).pack(side="left", ipady=3)

        ttk.Button(
            ctrl, text="▶  Run Comparison",
            style="Accent.TButton",
            command=self._on_compare
        ).pack(side="right")

        # Comparison gantt (reuses GanttChart component)
        self._compare_gantt = GanttChart(parent)
        self._compare_gantt.pack(fill="both", expand=True,
                                  padx=Spacing.CARD_PAD, pady=(0, Spacing.CARD_PAD))

        # Comparison table
        compare_cols = [
            ("algorithm",  "Algorithm",       160, "w"),
            ("avg_wt",     "Avg Wait",         80, "center"),
            ("avg_tat",    "Avg Turnaround",   110, "center"),
            ("avg_rt",     "Avg Response",     100, "center"),
            ("cpu",        "CPU Util %",        90, "center"),
            ("throughput", "Throughput",        90, "center"),
        ]
        col_ids = [c[0] for c in compare_cols]
        self._compare_tree = ttk.Treeview(
            parent,
            columns=col_ids,
            show="headings",
            height=6,
            style="Treeview"
        )
        for col_id, heading, width, anchor in compare_cols:
            self._compare_tree.heading(col_id, text=heading, anchor=anchor)
            self._compare_tree.column(col_id, width=width, anchor=anchor, minwidth=60, stretch=True)

        self._compare_tree.pack(fill="x", padx=Spacing.CARD_PAD, pady=(0, Spacing.CARD_PAD))

    def _build_statusbar(self):
        """Bottom status bar."""
        bar = tk.Frame(self.root, bg=Colors.BG_SECONDARY, height=28)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self._lbl_status = tk.Label(
            bar, text="  Ready — Add processes and select an algorithm to begin.",
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT_MUTED,
            font=Fonts.CAPTION, anchor="w"
        )
        self._lbl_status.pack(side="left", fill="x", expand=True)

        tk.Label(
            bar, text="KernelFlow v1.0  |  Python + Tkinter + Matplotlib  ",
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT_MUTED,
            font=Fonts.CAPTION, anchor="e"
        ).pack(side="right")

    # ─────────────────────────────────────────────
    #  Callbacks (from InputPanel)
    # ─────────────────────────────────────────────

    def _on_process_list_changed(self, processes: List[Process]):
        """Process list was added to or removed from — update the input table."""
        self._results_panel.update_process_list(processes)
        self._set_status(f"{len(processes)} process(es) in queue.")

    def _on_run(self, processes: List[Process], algorithm: str, quantum: int):
        """Run the selected simulation and push results to all panels."""
        try:
            result = run_simulation(processes, algorithm, time_quantum=quantum)
        except Exception as e:
            messagebox.showerror("Simulation Error", str(e), parent=self.root)
            self._input_panel.set_status_error(f"Error: {e}")
            return

        # ── Update Results Table ──────────────────
        self._results_panel.update_results(result.processes, algorithm)

        # ── Update Gantt Chart ────────────────────
        display_name = get_display_name(algorithm, quantum)
        self._gantt.render(result.gantt_blocks, result.processes, display_name)
        self._notebook.select(0)   # switch to Gantt tab automatically

        # ── Update Stats Panel ────────────────────
        desc = ALGO_DESCRIPTIONS.get(algorithm, "")
        self._stats_panel.update_stats(result.metrics, display_name, desc)

        # ── Update Ready Queue strip ──────────────
        # Show final state: all processes completed → empty queue
        self._stats_panel.update_queue([])

        # ── Status Bar ────────────────────────────
        avg_wt = result.metrics["avg_waiting_time"]
        cpu    = result.metrics["cpu_utilization"]
        self._set_status(
            f"✔  {display_name} complete — "
            f"Avg Waiting: {avg_wt} units  |  CPU Utilization: {cpu}%"
        )
        self._input_panel.set_status_success(
            f"Simulation complete. Avg WT = {avg_wt}"
        )

    def _on_reset(self):
        """Clear all results panels without touching the process list."""
        self._results_panel.clear_results()
        self._stats_panel.clear_stats()
        self._gantt.clear()
        self._set_status("Reset. Ready to run a new simulation.")

    def _on_compare(self):
        """Run all algorithms on the current process set and show comparison."""
        processes = self._input_panel.get_processes()
        if not processes:
            messagebox.showwarning(
                "No Processes",
                "Add at least one process before running the comparison.",
                parent=self.root
            )
            return

        try:
            quantum = int(self._var_compare_quantum.get())
        except ValueError:
            quantum = 2

        try:
            results = run_comparison(processes, time_quantum=quantum)
        except Exception as e:
            messagebox.showerror("Comparison Error", str(e), parent=self.root)
            return

        # ── Populate comparison table ─────────────
        for row in self._compare_tree.get_children():
            self._compare_tree.delete(row)

        best_wt  = min(r.metrics["avg_waiting_time"]    for r in results.values())
        best_tat = min(r.metrics["avg_turnaround_time"] for r in results.values())

        for i, (name, res) in enumerate(results.items()):
            m    = res.metrics
            tag  = f"row_{i}"
            color = Colors.get_process_color(i)
            self._compare_tree.tag_configure(tag, foreground=color)

            # Mark best values with ★
            wt_str  = f"{m['avg_waiting_time']} ★" if m['avg_waiting_time']  == best_wt  else str(m['avg_waiting_time'])
            tat_str = f"{m['avg_turnaround_time']} ★" if m['avg_turnaround_time'] == best_tat else str(m['avg_turnaround_time'])

            self._compare_tree.insert(
                "", "end",
                values=(
                    name,
                    wt_str,
                    tat_str,
                    m["avg_response_time"],
                    f"{m['cpu_utilization']}%",
                    m["throughput"],
                ),
                tags=(tag,)
            )

        # ── Render comparison bar chart ────────────
        compare_metrics = {name: res.metrics for name, res in results.items()}
        self._compare_gantt.render_comparison(compare_metrics)

        self._notebook.select(1)   # switch to Compare tab
        self._set_status(
            f"Comparison complete — {len(results)} algorithms, "
            f"{len(processes)} processes. ★ marks best values."
        )

    # ─────────────────────────────────────────────
    #  Helpers
    # ─────────────────────────────────────────────

    def _set_status(self, message: str):
        self._lbl_status.config(text=f"  {message}")

    def _on_close(self):
        """Clean shutdown."""
        plt = None
        try:
            import matplotlib.pyplot as plt_mod
            plt_mod.close("all")
        except Exception:
            pass
        self.root.destroy()
