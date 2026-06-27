"""
algorithms/sjf.py
=================
Shortest Job First (SJF) Scheduling Algorithm.

Supports two modes (set via constructor):
  preemptive=False  → Non-preemptive SJF (classic)
      At each decision point, pick the arrived process with shortest burst.
      Once started, the process runs to completion.

  preemptive=True   → Preemptive SJF = SRTF (Shortest Remaining Time First)
      At every clock tick, if a newly arrived process has shorter remaining
      time than the running process, preempt and switch.

Characteristics:
  - Optimal average waiting time among non-preemptive algorithms (non-preemptive)
  - SRTF gives minimum possible average waiting time overall
  - May cause starvation of long processes if short ones keep arriving
  - Requires knowledge of burst time (not always realistic)

Example Non-Preemptive (demo):
  P1: arrival=0 burst=5  → starts at 0 (only arrived process)
  P2: arrival=1 burst=3  → starts at 5 (shortest of P2, P3)
  P3: arrival=2 burst=8  → starts at 8
  Order: P1 → P2 → P3
"""

from typing import List, Optional
from .base_algorithm import BaseAlgorithm
from models.process import Process


class SJF(BaseAlgorithm):

    def __init__(self, preemptive: bool = False):
        """
        Args:
            preemptive : False = non-preemptive SJF (default)
                         True  = preemptive SRTF
        """
        self.preemptive  = preemptive
        self.name        = "SJF (Preemptive)" if preemptive else "SJF"
        self.description = (
            "Shortest Remaining Time First — preemptive."
            if preemptive else
            "Shortest Job First — non-preemptive, lowest burst time wins."
        )

    # ─────────────────────────────────────────────
    #  Public Interface
    # ─────────────────────────────────────────────

    def run(self, processes: List[Process]) -> List[Process]:
        """Dispatch to the correct implementation based on mode."""
        if not processes:
            raise ValueError("SJF: process list is empty.")

        if self.preemptive:
            return self._run_preemptive(processes)
        else:
            return self._run_non_preemptive(processes)

    # ─────────────────────────────────────────────
    #  Non-Preemptive SJF
    # ─────────────────────────────────────────────

    def _run_non_preemptive(self, processes: List[Process]) -> List[Process]:
        """
        Non-preemptive SJF:
          At each scheduling decision, select the arrived process
          with the minimum burst_time. Run it to completion.
        """
        procs       = self.prepare_processes(processes)
        completed   = set()
        current_time = 0
        n           = len(procs)

        while len(completed) < n:
            # Gather all processes that have arrived and aren't done
            available = self.get_arrived(procs, current_time, completed)

            if not available:
                # CPU idle — jump to next arrival
                current_time = self.next_arrival(procs, completed)
                continue

            # Pick shortest burst; break ties by arrival time then PID
            chosen = min(available, key=lambda p: (p.burst_time, p.arrival_time, p.pid))

            # Record first CPU access
            chosen.start_time    = current_time
            chosen.response_time = current_time - chosen.arrival_time

            # Run to completion
            current_time         += chosen.burst_time
            chosen.completion_time = current_time
            chosen.remaining_time  = 0

            chosen.gantt_blocks.append((chosen.start_time, chosen.completion_time))
            chosen.calculate_times()
            completed.add(chosen.pid)

        return procs

    # ─────────────────────────────────────────────
    #  Preemptive SJF (SRTF)
    # ─────────────────────────────────────────────

    def _run_preemptive(self, processes: List[Process]) -> List[Process]:
        """
        Preemptive SRTF:
          Each clock tick, re-evaluate which arrived process has the
          shortest *remaining* time. Preempt the current process if needed.
          Build gantt_blocks by recording consecutive runs as one block.
        """
        procs        = self.prepare_processes(processes)
        completed    = set()
        current_time = 0
        n            = len(procs)

        # Gantt tracking: (current process, block_start)
        running_pid:   Optional[str] = None
        block_start:   int           = 0

        while len(completed) < n:
            available = self.get_arrived(procs, current_time, completed)

            if not available:
                # Flush any open Gantt block before idle jump
                if running_pid is not None:
                    p = next(x for x in procs if x.pid == running_pid)
                    p.gantt_blocks.append((block_start, current_time))
                    running_pid = None

                current_time = self.next_arrival(procs, completed)
                continue

            # Pick shortest remaining time; ties → arrival time → PID
            chosen = min(
                available,
                key=lambda p: (p.remaining_time, p.arrival_time, p.pid)
            )

            # Track response time on first execution
            if chosen.start_time == -1:
                chosen.start_time    = current_time
                chosen.response_time = current_time - chosen.arrival_time

            # If a different process is now chosen, close the previous Gantt block
            if running_pid != chosen.pid:
                if running_pid is not None:
                    prev = next(x for x in procs if x.pid == running_pid)
                    prev.gantt_blocks.append((block_start, current_time))
                block_start = current_time
                running_pid = chosen.pid

            # Advance one tick
            chosen.remaining_time -= 1
            current_time          += 1

            # Check for completion
            if chosen.remaining_time == 0:
                chosen.completion_time = current_time
                chosen.gantt_blocks.append((block_start, current_time))
                running_pid = None
                chosen.calculate_times()
                completed.add(chosen.pid)

        return procs
