import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, List, Optional

from models.process import create_process, Process
from utils.validators import (
    validate_process_form,
    validate_process_list,
    validate_algorithm_selection,
    validate_time_quantum,
)
from ui.theme import Colors, Fonts, Spacing, Styles
from utils.scheduler import ALGORITHM_NAMES


class InputPanel(ttk.Frame):


    def __init__(
        self,
        parent,
        on_run:    Callable,
        on_reset:  Callable,
        on_process_list_changed: Callable,
        **kwargs
    ):
        super().__init__(parent, style="Card.TFrame", **kwargs)
        self.on_run                   = on_run
        self.on_reset                 = on_reset
        self.on_process_list_changed  = on_process_list_changed

        self._processes: List[Process] = []
        self._pid_counter: int         = 1    # auto-increment for default PID

        self._build_ui()
        self._set_initial_values()


    def _build_ui(self):
        self.configure(padding=Spacing.CARD_PAD)

        # ── Header ────────────────────────────────
        hdr = tk.Label(
            self, text="⚙  Process Manager",
            bg=Colors.BG_SECONDARY, fg=Colors.ACCENT,
            font=Fonts.HEADING_3, anchor="w"
        )
        hdr.pack(fill="x", pady=(0, Spacing.MD))

        self._divider()

        # ── Process Input Form ────────────────────
        form_lbl = tk.Label(
            self, text="ADD PROCESS",
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT_MUTED,
            font=(Fonts.FAMILY, Fonts.SIZE_XS, "bold"), anchor="w"
        )
        form_lbl.pack(fill="x", pady=(Spacing.SM, Spacing.XS))

        form = tk.Frame(self, bg=Colors.BG_SECONDARY)
        form.pack(fill="x")

        # Field definitions: (label, var_name, default)
        fields = [
            ("Process ID",    "_var_pid",     "P1"),
            ("Arrival Time",  "_var_arrival", "0"),
            ("Burst Time",    "_var_burst",   "5"),
            ("Priority",      "_var_priority","1"),
        ]

        self._entry_refs = {}   # var_name → Entry widget (for error highlighting)

        for label_text, var_name, default in fields:
            setattr(self, var_name, tk.StringVar(value=default))
            row = tk.Frame(form, bg=Colors.BG_SECONDARY)
            row.pack(fill="x", pady=Spacing.XS)

            tk.Label(
                row, text=label_text, width=12, anchor="w",
                bg=Colors.BG_SECONDARY, fg=Colors.TEXT_SECONDARY,
                font=Fonts.CAPTION
            ).pack(side="left")

            entry = tk.Entry(
                row, textvariable=getattr(self, var_name),
                **Styles.ENTRY, width=14
            )
            entry.pack(side="left", padx=(Spacing.XS, 0), ipady=Spacing.XS)
            self._entry_refs[var_name] = entry

        # ── Add Button ────────────────────────────
        add_btn = ttk.Button(
            self, text="＋  Add Process",
            style="Accent.TButton",
            command=self._add_process
        )
        add_btn.pack(fill="x", pady=(Spacing.SM, 0))

        # Keyboard shortcut: Enter → Add
        self.bind_all("<Return>", lambda e: self._add_process())

        self._divider(pady=Spacing.MD)

        # ── Process Counter Badge ─────────────────
        badge_row = tk.Frame(self, bg=Colors.BG_SECONDARY)
        badge_row.pack(fill="x", pady=(0, Spacing.XS))

        tk.Label(
            badge_row, text="Processes in queue:",
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT_SECONDARY,
            font=Fonts.CAPTION
        ).pack(side="left")

        self._lbl_count = tk.Label(
            badge_row, text="0",
            bg=Colors.BG_SECONDARY, fg=Colors.ACCENT,
            font=Fonts.LABEL_BOLD
        )
        self._lbl_count.pack(side="left", padx=Spacing.XS)

        # Remove last + Clear all
        btn_row = tk.Frame(self, bg=Colors.BG_SECONDARY)
        btn_row.pack(fill="x", pady=(0, Spacing.XS))

        ttk.Button(
            btn_row, text="Remove Last",
            style="TButton",
            command=self._remove_last
        ).pack(side="left", expand=True, fill="x", padx=(0, Spacing.XS))

        ttk.Button(
            btn_row, text="Clear All",
            style="Danger.TButton",
            command=self._clear_all
        ).pack(side="left", expand=True, fill="x")

        self._divider(pady=Spacing.MD)

        # ── Algorithm Selection ───────────────────
        algo_lbl = tk.Label(
            self, text="ALGORITHM",
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT_MUTED,
            font=(Fonts.FAMILY, Fonts.SIZE_XS, "bold"), anchor="w"
        )
        algo_lbl.pack(fill="x", pady=(0, Spacing.XS))

        self._var_algorithm = tk.StringVar(value=ALGORITHM_NAMES[0])
        algo_cb = ttk.Combobox(
            self,
            textvariable=self._var_algorithm,
            values=ALGORITHM_NAMES,
            state="readonly",
            font=Fonts.BODY,
        )
        algo_cb.pack(fill="x", ipady=Spacing.XS)
        algo_cb.bind("<<ComboboxSelected>>", self._on_algorithm_changed)

        # ── Time Quantum (Round Robin only) ───────
        self._quantum_frame = tk.Frame(self, bg=Colors.BG_SECONDARY)
        self._quantum_frame.pack(fill="x", pady=(Spacing.SM, 0))

        tk.Label(
            self._quantum_frame, text="Time Quantum:",
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT_SECONDARY,
            font=Fonts.CAPTION
        ).pack(side="left")

        self._var_quantum = tk.StringVar(value="2")
        self._entry_quantum = tk.Entry(
            self._quantum_frame,
            textvariable=self._var_quantum,
            **Styles.ENTRY, width=6
        )
        self._entry_quantum.pack(side="left", padx=(Spacing.XS, 0), ipady=Spacing.XS)

        tk.Label(
            self._quantum_frame, text="units",
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT_MUTED,
            font=Fonts.CAPTION
        ).pack(side="left", padx=(Spacing.XS, 0))

        # Hide quantum row initially (FCFS is default)
        self._quantum_frame.pack_forget()

        self._divider(pady=Spacing.MD)

        # ── Action Buttons ────────────────────────
        run_btn = ttk.Button(
            self, text="▶  Run Simulation",
            style="Accent.TButton",
            command=self._run_simulation
        )
        run_btn.pack(fill="x", pady=(0, Spacing.XS))

        reset_btn = ttk.Button(
            self, text="↺  Reset",
            style="TButton",
            command=self._reset
        )
        reset_btn.pack(fill="x")

        # ── Info footer ───────────────────────────
        self._lbl_status = tk.Label(
            self, text="Add processes then run the simulation.",
            bg=Colors.BG_SECONDARY, fg=Colors.TEXT_MUTED,
            font=Fonts.CAPTION, wraplength=200, justify="left"
        )
        self._lbl_status.pack(fill="x", pady=(Spacing.LG, 0))

    # ─────────────────────────────────────────────
    #  Helper Widgets
    # ─────────────────────────────────────────────

    def _divider(self, pady=Spacing.SM):
        tk.Frame(self, bg=Colors.BORDER, height=1).pack(fill="x", pady=pady)

    # ─────────────────────────────────────────────
    #  Event Handlers
    # ─────────────────────────────────────────────

    def _set_initial_values(self):
        """Pre-fill PID with auto-incremented default."""
        self._var_pid.set(f"P{self._pid_counter}")

    def _on_algorithm_changed(self, event=None):
        """Show/hide the Time Quantum row based on algorithm selection."""
        algo = self._var_algorithm.get()
        if algo == "Round Robin":
            self._quantum_frame.pack(fill="x", pady=(Spacing.SM, 0))
        else:
            self._quantum_frame.pack_forget()

    def _add_process(self):
        """Validate form inputs and add a Process to the internal list."""
        pid      = self._var_pid.get().strip()
        arrival  = self._var_arrival.get().strip()
        burst    = self._var_burst.get().strip()
        priority = self._var_priority.get().strip()

        existing_pids = [p.pid for p in self._processes]
        result = validate_process_form(pid, arrival, burst, priority, existing_pids)

        if not result.ok:
            self._show_error(result.message, result.field)
            return

        # Create and append the process
        process = create_process(pid, int(arrival), int(burst), int(priority))
        self._processes.append(process)

        # Clear error styling
        self._clear_error_styles()

        # Update counter
        self._lbl_count.config(text=str(len(self._processes)))

        # Auto-increment PID for next entry
        self._pid_counter += 1
        self._var_pid.set(f"P{self._pid_counter}")
        self._var_arrival.set("0")
        self._var_burst.set("5")
        self._var_priority.set("1")

        # Notify parent
        self.on_process_list_changed(list(self._processes))
        self._set_status(f"Process {pid} added. ({len(self._processes)} total)", Colors.SUCCESS)

    def _remove_last(self):
        """Remove the most recently added process."""
        if not self._processes:
            self._set_status("No processes to remove.", Colors.WARNING)
            return
        removed = self._processes.pop()
        self._pid_counter = max(1, self._pid_counter - 1)
        self._var_pid.set(f"P{self._pid_counter}")
        self._lbl_count.config(text=str(len(self._processes)))
        self.on_process_list_changed(list(self._processes))
        self._set_status(f"Removed {removed.pid}.", Colors.WARNING)

    def _clear_all(self):
        """Remove all processes after confirmation."""
        if not self._processes:
            return
        if messagebox.askyesno(
            "Clear All Processes",
            f"Remove all {len(self._processes)} processes?",
            parent=self
        ):
            self._processes.clear()
            self._pid_counter = 1
            self._var_pid.set("P1")
            self._lbl_count.config(text="0")
            self.on_process_list_changed([])
            self.on_reset()
            self._set_status("All processes cleared.", Colors.DANGER)

    def _run_simulation(self):
        """Validate process list and algorithm, then trigger the simulation."""
        list_result = validate_process_list(self._processes)
        if not list_result.ok:
            self._set_status(list_result.message, Colors.DANGER)
            messagebox.showerror("Cannot Run", list_result.message, parent=self)
            return

        algo    = self._var_algorithm.get()
        quantum = self._var_quantum.get().strip()

        algo_result = validate_algorithm_selection(algo, quantum)
        if not algo_result.ok:
            self._set_status(algo_result.message, Colors.DANGER)
            messagebox.showerror("Invalid Algorithm", algo_result.message, parent=self)
            return

        quantum_int = int(quantum) if algo == "Round Robin" else 2
        self._set_status(f"Running {algo}…", Colors.INFO)
        self.on_run(list(self._processes), algo, quantum_int)

    def _reset(self):
        """Reset results without clearing the process list."""
        self.on_reset()
        self._set_status("Results cleared. Ready to run.", Colors.TEXT_SECONDARY)

    # ─────────────────────────────────────────────
    #  Status & Error Helpers
    # ─────────────────────────────────────────────

    def _set_status(self, message: str, color: str = Colors.TEXT_MUTED):
        self._lbl_status.config(text=message, fg=color)

    def _show_error(self, message: str, field: str = ""):
        """Highlight the offending field and show the error message."""
        self._clear_error_styles()
        field_map = {
            "pid":      "_var_pid",
            "arrival":  "_var_arrival",
            "burst":    "_var_burst",
            "priority": "_var_priority",
            "quantum":  None,
        }
        var_name = field_map.get(field)
        if var_name and var_name in self._entry_refs:
            entry = self._entry_refs[var_name]
            entry.config(highlightbackground=Colors.DANGER, highlightcolor=Colors.DANGER)
        self._set_status(f"⚠  {message}", Colors.DANGER)

    def _clear_error_styles(self):
        """Remove error highlight from all entry fields."""
        for entry in self._entry_refs.values():
            entry.config(
                highlightbackground=Colors.BORDER,
                highlightcolor=Colors.ACCENT
            )


    def get_processes(self) -> List[Process]:
        return list(self._processes)

    def get_algorithm(self) -> str:
        return self._var_algorithm.get()

    def get_quantum(self) -> int:
        try:
            return int(self._var_quantum.get())
        except ValueError:
            return 2

    def set_status_success(self, message: str):
        self._set_status(message, Colors.SUCCESS)

    def set_status_error(self, message: str):
        self._set_status(message, Colors.DANGER)
