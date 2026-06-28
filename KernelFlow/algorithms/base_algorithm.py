"""
algorithms/base_algorithm.py
============================
Abstract base class that defines the plugin contract for all scheduling algorithms.

Design Pattern: Template Method + Strategy
  - Every algorithm MUST implement run()
  - Shared helpers (copy_processes, get_arrived) live here once
  - Adding a new algorithm = subclass + one line in scheduler.py REGISTRY

Plugin Contract:
  1. Subclass BaseAlgorithm
  2. Implement run(processes) -> list[Process]
  3. Register in utils/scheduler.py ALGORITHM_REGISTRY
"""

from abc import ABC, abstractmethod
from copy import deepcopy
from typing import List
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.process import Process


class BaseAlgorithm(ABC):
    """
    Abstract base for all CPU scheduling algorithms.

    Subclasses must implement:
        run(processes) -> List[Process]

    Subclasses may override:
        name        : Human-readable algorithm name (used in UI labels)
        description : One-line description (used in tooltips)
    """

    name:        str = "Base Algorithm"
    description: str = "Abstract base — do not instantiate directly."

    # ─────────────────────────────────────────────
    #  Abstract Interface
    # ─────────────────────────────────────────────

    @abstractmethod
    def run(self, processes: List[Process]) -> List[Process]:
        """
        Execute the scheduling algorithm on the given process list.

        Args:
            processes : List of Process objects with input fields set.
                        These are COPIES — original list is never mutated.

        Returns:
            The same list of Process objects with all computed fields populated:
              start_time, completion_time, waiting_time,
              turnaround_time, response_time, gantt_blocks

        Raises:
            ValueError : If processes list is empty or malformed.
        """
        raise NotImplementedError

    # ─────────────────────────────────────────────
    #  Shared Helpers (available to all subclasses)
    # ─────────────────────────────────────────────

    def prepare_processes(self, processes: List[Process]) -> List[Process]:
        """
        Deep-copies process list and resets all computed fields.
        Always call this at the start of run() to avoid mutating the originals.
        """
        copies = deepcopy(processes)
        for p in copies:
            p.reset_computed_fields()
        return copies

    def get_arrived(
        self,
        processes: List[Process],
        current_time: int,
        completed: set
    ) -> List[Process]:
        """
        Returns processes that have arrived by current_time and are not completed.

        Args:
            processes    : Full process list
            current_time : Current simulation clock tick
            completed    : Set of PIDs already finished

        Returns:
            Filtered list of eligible processes
        """
        return [
            p for p in processes
            if p.arrival_time <= current_time and p.pid not in completed
        ]

    def next_arrival(self, processes: List[Process], completed: set) -> int:
        """
        Returns the earliest arrival time among unfinished processes.
        Used to fast-forward the clock when the CPU is idle.
        """
        pending = [p for p in processes if p.pid not in completed]
        if not pending:
            return -1
        return min(p.arrival_time for p in pending)

    def build_gantt_summary(self, processes: List[Process]) -> List[dict]:
        """
        Flattens all gantt_blocks across all processes into a single
        chronological list used by the Gantt chart renderer.

        Returns:
            List of dicts: [{"pid": str, "start": int, "end": int}, ...]
            Sorted by start time.
        """
        blocks = []
        for p in processes:
            for (start, end) in p.gantt_blocks:
                blocks.append({"pid": p.pid, "start": start, "end": end})
        return sorted(blocks, key=lambda b: b["start"])
