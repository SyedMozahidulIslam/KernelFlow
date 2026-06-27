"""
algorithms/fcfs.py
==================
First Come First Serve (FCFS) Scheduling Algorithm.

Behaviour:
  - Non-preemptive: once a process starts, it runs to completion
  - Processes are ordered strictly by arrival time
  - Ties in arrival time are broken by PID (alphabetical) for determinism

Characteristics:
  - Simple and fair in order of arrival
  - Suffers from the "Convoy Effect": long processes block shorter ones
  - No starvation (every process eventually runs)

Example (from the UI demo):
  P1: arrival=0, burst=5  → runs 0–5
  P2: arrival=1, burst=3  → runs 5–8
  P3: arrival=2, burst=8  → runs 8–16
"""

from typing import List
from .base_algorithm import BaseAlgorithm
from models.process import Process


class FCFS(BaseAlgorithm):

    name        = "FCFS"
    description = "First Come First Serve — non-preemptive, ordered by arrival time."

    def run(self, processes: List[Process]) -> List[Process]:
        """
        Execute FCFS scheduling.

        Steps:
          1. Sort by arrival time (then PID for tie-breaking)
          2. Walk through processes in order
          3. If CPU is idle, fast-forward clock to next arrival
          4. Run each process to completion (non-preemptive)
          5. Calculate all timing fields

        Returns:
            processes list with all computed fields populated.
        """
        if not processes:
            raise ValueError("FCFS: process list is empty.")

        # Work on deep copies — never mutate the originals
        procs = self.prepare_processes(processes)

        # Sort by arrival time; break ties by PID for determinism
        procs.sort(key=lambda p: (p.arrival_time, p.pid))

        current_time = 0

        for p in procs:
            # If CPU is idle (next process hasn't arrived yet), advance the clock
            if current_time < p.arrival_time:
                current_time = p.arrival_time

            # Record when this process first gets the CPU
            p.start_time    = current_time
            p.response_time = current_time - p.arrival_time

            # Run to completion (non-preemptive)
            current_time       += p.burst_time
            p.completion_time   = current_time
            p.remaining_time    = 0

            # Store the single execution block for the Gantt chart
            p.gantt_blocks.append((p.start_time, p.completion_time))

            # Derive WT and TAT
            p.calculate_times()

        return procs
