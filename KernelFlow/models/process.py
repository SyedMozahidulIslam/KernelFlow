"""
models/process.py
=================
Defines the Process data model used across the entire KernelFlow application.

This is the single shared object that travels through every layer:
  Input Panel → Algorithm → Metrics → UI (Results Table, Gantt, Stats)

Design:
  - Uses @dataclass for clean, readable field declarations
  - All input fields are set at creation time
  - All computed fields default to -1 (sentinel = "not yet calculated")
  - Provides helper methods used by the Gantt chart and results table
"""

from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────
#  Process Model
# ─────────────────────────────────────────────

@dataclass
class Process:
    """
    Represents a single OS process in the scheduling simulation.

    Input Fields (user-provided):
        pid          : Unique process identifier string (e.g. "P1")
        arrival_time : Time at which the process enters the ready queue
        burst_time   : Total CPU time the process requires to complete
        priority     : Scheduling priority (lower number = higher priority)

    Computed Fields (filled by algorithm):
        start_time        : First time the CPU began executing this process
        completion_time   : Time at which the process finished execution
        waiting_time      : Total time spent waiting in the ready queue
        turnaround_time   : Total time from arrival to completion
        response_time     : Time from arrival to first CPU response
        remaining_time    : Used internally by preemptive algorithms
        gantt_blocks      : List of (start, end) tuples for Gantt chart rendering
    """

    # ── Input Fields ──────────────────────────────────────
    pid:          str
    arrival_time: int
    burst_time:   int
    priority:     int = 0          # default priority = 0 (lowest)

    # ── Computed Fields (sentinel = -1 means not yet set) ─
    start_time:      int = field(default=-1, init=False)
    completion_time: int = field(default=-1, init=False)
    waiting_time:    int = field(default=-1, init=False)
    turnaround_time: int = field(default=-1, init=False)
    response_time:   int = field(default=-1, init=False)

    # ── Internal / Algorithm State ─────────────────────────
    remaining_time: int            = field(default=-1, init=False)
    gantt_blocks:   list           = field(default_factory=list, init=False)
    # gantt_blocks stores [(start_time, end_time), ...] for multi-block rendering

    def __post_init__(self):
        """Called automatically after __init__. Initialises derived state."""
        # remaining_time starts equal to burst_time; decremented by preemptive algos
        self.remaining_time = self.burst_time

    # ─────────────────────────────────────────────
    #  Computed Properties
    # ─────────────────────────────────────────────

    @property
    def is_completed(self) -> bool:
        """Returns True if the process has finished execution."""
        return self.remaining_time == 0

    @property
    def has_arrived(self, current_time: int = 0) -> bool:
        """Returns True if the process has arrived by a given time."""
        return self.arrival_time <= current_time

    # ─────────────────────────────────────────────
    #  Calculation Helpers (called by metrics.py)
    # ─────────────────────────────────────────────

    def calculate_times(self) -> None:
        """
        Derives waiting_time and turnaround_time from completion and start times.
        Must be called AFTER completion_time and start_time are set by the algorithm.

        Formulas:
            Turnaround Time = Completion Time - Arrival Time
            Waiting Time    = Turnaround Time - Burst Time
            Response Time   = Start Time      - Arrival Time
              (start_time must be set separately for preemptive algorithms)
        """
        if self.completion_time == -1:
            raise ValueError(
                f"Process {self.pid}: completion_time not set before calling calculate_times()"
            )

        self.turnaround_time = self.completion_time - self.arrival_time
        self.waiting_time    = self.turnaround_time - self.burst_time

        # Response time: use start_time if set, else treat first gantt block as start
        if self.start_time != -1:
            self.response_time = self.start_time - self.arrival_time
        elif self.gantt_blocks:
            self.response_time = self.gantt_blocks[0][0] - self.arrival_time
        else:
            self.response_time = self.waiting_time   # fallback

    # ─────────────────────────────────────────────
    #  Reset (used by the Reset button in the UI)
    # ─────────────────────────────────────────────

    def reset_computed_fields(self) -> None:
        """
        Resets all computed/algorithm fields back to their sentinel values.
        Keeps input fields (pid, arrival_time, burst_time, priority) intact.
        Called when the user clicks Reset or changes the algorithm.
        """
        self.start_time      = -1
        self.completion_time = -1
        self.waiting_time    = -1
        self.turnaround_time = -1
        self.response_time   = -1
        self.remaining_time  = self.burst_time   # restore to original
        self.gantt_blocks    = []

    # ─────────────────────────────────────────────
    #  Representation Helpers
    # ─────────────────────────────────────────────

    def to_dict(self) -> dict:
        """
        Serialises all fields to a plain dictionary.
        Used by the results table and export functions.
        """
        return {
            "PID":             self.pid,
            "Arrival Time":    self.arrival_time,
            "Burst Time":      self.burst_time,
            "Priority":        self.priority,
            "Start Time":      self.start_time,
            "Completion Time": self.completion_time,
            "Waiting Time":    self.waiting_time,
            "Turnaround Time": self.turnaround_time,
            "Response Time":   self.response_time,
        }

    def to_table_row(self) -> tuple:
        """
        Returns a tuple of display-ready values for the ttk.Treeview table.
        Computed fields show '—' if not yet calculated (sentinel = -1).
        """
        def fmt(val: int) -> str:
            return str(val) if val != -1 else "—"

        return (
            self.pid,
            fmt(self.arrival_time),
            fmt(self.burst_time),
            fmt(self.priority),
            fmt(self.completion_time),
            fmt(self.waiting_time),
            fmt(self.turnaround_time),
            fmt(self.response_time),
        )

    def __repr__(self) -> str:
        return (
            f"Process(pid={self.pid!r}, "
            f"arrival={self.arrival_time}, "
            f"burst={self.burst_time}, "
            f"priority={self.priority}, "
            f"CT={self.completion_time}, "
            f"WT={self.waiting_time}, "
            f"TAT={self.turnaround_time})"
        )


# ─────────────────────────────────────────────
#  Factory Helper
# ─────────────────────────────────────────────

def create_process(pid: str, arrival: int, burst: int, priority: int = 0) -> Process:
    """
    Convenience factory function — thin wrapper around Process().
    Keeps call sites clean and provides a single place for future defaults.

    Args:
        pid      : Process identifier (e.g. "P1")
        arrival  : Arrival time (non-negative integer)
        burst    : CPU burst time (positive integer)
        priority : Priority level (default 0 = lowest)

    Returns:
        A freshly initialised Process instance
    """
    return Process(
        pid=str(pid),
        arrival_time=int(arrival),
        burst_time=int(burst),
        priority=int(priority)
    )
