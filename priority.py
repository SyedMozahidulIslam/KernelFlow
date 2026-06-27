"""
algorithms/priority.py
======================
Priority Scheduling Algorithm.

Supports two modes (set via constructor):
  preemptive=False  → Non-preemptive Priority
      At each scheduling decision, pick the highest-priority arrived process.
      Once started, runs to completion even if a higher-priority process arrives.

  preemptive=True   → Preemptive Priority
      At every tick, re-evaluate. If a higher-priority process arrives while
      another is running, immediately preempt and switch.

Priority Convention:
  LOWER number = HIGHER priority (standard OS convention: 0 is most urgent)
  This matches Linux nice values and most textbook definitions.

Starvation:
  Low-priority processes can starve if high-priority ones keep arriving.
  Mitigation (future): aging — increase priority over time (not implemented in v1).

Example Non-Preemptive:
  P1: arrival=0, burst=5, priority=2
  P2: arrival=1, burst=3, priority=1   ← highest priority (lowest number)
  P3: arrival=2, burst=8, priority=3
  Order: P1 (alone at t=0) → P2 (priority 1 beats P3) → P3
"""

from typing import List, Optional
from .base_algorithm import BaseAlgorithm
from models.process import Process


class Priority(BaseAlgorithm):

    def __init__(self, preemptive: bool = False):
        """
        Args:
            preemptive : False = non-preemptive (default), True = preemptive
        """
        self.preemptive  = preemptive
        self.name        = "Priority (Preemptive)" if preemptive else "Priority"
        self.description = (
            "Priority Scheduling — preemptive, lower number = higher priority."
            if preemptive else
            "Priority Scheduling — non-preemptive, lower number = higher priority."
        )

    # ─────────────────────────────────────────────
    #  Public Interface
    # ─────────────────────────────────────────────

    def run(self, processes: List[Process]) -> List[Process]:
        """Dispatch to correct implementation based on mode."""
        if not processes:
            raise ValueError("Priority: process list is empty.")

        if self.preemptive:
            return self._run_preemptive(processes)
        else:
            return self._run_non_preemptive(processes)

    # ─────────────────────────────────────────────
    #  Non-Preemptive Priority
    # ─────────────────────────────────────────────

    def _run_non_preemptive(self, processes: List[Process]) -> List[Process]:
        """
        At each scheduling point, pick the arrived process with
        the lowest priority number (= highest urgency).
        Run it to completion before re-evaluating.

        Tie-breaking: arrival_time → pid (for determinism)
        """
        procs        = self.prepare_processes(processes)
        completed    = set()
        current_time = 0
        n            = len(procs)

        while len(completed) < n:
            available = self.get_arrived(procs, current_time, completed)

            if not available:
                current_time = self.next_arrival(procs, completed)
                continue

            # Lowest priority number = highest urgency
            chosen = min(available, key=lambda p: (p.priority, p.arrival_time, p.pid))

            chosen.start_time    = current_time
            chosen.response_time = current_time - chosen.arrival_time

            current_time          += chosen.burst_time
            chosen.completion_time = current_time
            chosen.remaining_time  = 0

            chosen.gantt_blocks.append((chosen.start_time, chosen.completion_time))
            chosen.calculate_times()
            completed.add(chosen.pid)

        return procs

    # ─────────────────────────────────────────────
    #  Preemptive Priority
    # ─────────────────────────────────────────────

    def _run_preemptive(self, processes: List[Process]) -> List[Process]:
        """
        At every clock tick, select the arrived process with the lowest
        priority number. Preempt the current process if a better one arrives.
        Builds granular gantt_blocks for each continuous run segment.
        """
        procs        = self.prepare_processes(processes)
        completed    = set()
        current_time = 0
        n            = len(procs)

        running_pid: Optional[str] = None
        block_start: int           = 0

        while len(completed) < n:
            available = self.get_arrived(procs, current_time, completed)

            if not available:
                # Flush open Gantt block before idle jump
                if running_pid is not None:
                    p = next(x for x in procs if x.pid == running_pid)
                    p.gantt_blocks.append((block_start, current_time))
                    running_pid = None

                current_time = self.next_arrival(procs, completed)
                continue

            # Select highest priority (lowest number); tie → arrival → pid
            chosen = min(available, key=lambda p: (p.priority, p.arrival_time, p.pid))

            # Record first response
            if chosen.start_time == -1:
                chosen.start_time    = current_time
                chosen.response_time = current_time - chosen.arrival_time

            # Preemption check: different process selected
            if running_pid != chosen.pid:
                if running_pid is not None:
                    prev = next(x for x in procs if x.pid == running_pid)
                    prev.gantt_blocks.append((block_start, current_time))
                block_start = current_time
                running_pid = chosen.pid

            # Run one tick
            chosen.remaining_time -= 1
            current_time          += 1

            if chosen.remaining_time == 0:
                chosen.completion_time = current_time
                chosen.gantt_blocks.append((block_start, current_time))
                running_pid = None
                chosen.calculate_times()
                completed.add(chosen.pid)

        return procs
