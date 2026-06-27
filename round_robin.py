"""
algorithms/round_robin.py
=========================
Round Robin (RR) Scheduling Algorithm.

Behaviour:
  - Preemptive: each process gets a fixed time slice (quantum)
  - If a process doesn't finish within its quantum, it's moved to
    the back of the ready queue and the next process runs
  - New arrivals are added to the queue in arrival-time order
  - Process that exhausts its quantum is re-queued AFTER new arrivals
    at the same tick (standard OS convention)

Characteristics:
  - Fair: every process gets equal CPU time slices
  - Good response time for interactive systems
  - Higher context-switch overhead than non-preemptive algorithms
  - Performance heavily dependent on quantum size

Queue Management (important edge case):
  When a process finishes exactly at a quantum boundary AND new processes
  arrive at that same tick, the new arrivals go into the queue first
  (they were waiting), then the re-queued process goes after.

Example (quantum=2):
  P1: arrival=0, burst=5
  P2: arrival=1, burst=3
  P3: arrival=2, burst=8
  Timeline: P1(0-2) → P2(2-4) → P3(4-6) → P1(6-8) → P2(8-9) → P3(9-11) → P1(11-12) → P3(12-16)
"""

from collections import deque
from typing import List, Optional
from .base_algorithm import BaseAlgorithm
from models.process import Process


class RoundRobin(BaseAlgorithm):

    name        = "Round Robin"
    description = "Round Robin — preemptive, fixed time quantum, fair CPU sharing."

    def __init__(self, time_quantum: int = 2):
        """
        Args:
            time_quantum : CPU time slice per turn (positive integer, default=2)
        """
        if time_quantum < 1:
            raise ValueError(f"RoundRobin: time_quantum must be >= 1, got {time_quantum}")
        self.time_quantum = time_quantum

    def run(self, processes: List[Process]) -> List[Process]:
        """
        Execute Round Robin scheduling.

        Algorithm:
          1. Sort all processes by arrival time
          2. Maintain a ready queue (deque for O(1) append/pop)
          3. At each step:
             a. Run current process for min(quantum, remaining_time) ticks
             b. Add any newly arrived processes to the queue
             c. If current process is not done, re-queue it
             d. Pick next from the front of the queue
          4. If queue is empty and processes remain, fast-forward clock

        Returns:
            processes list with all computed fields and gantt_blocks populated.
        """
        if not processes:
            raise ValueError("RoundRobin: process list is empty.")

        procs = self.prepare_processes(processes)
        # Sort by arrival for clean queue seeding
        procs.sort(key=lambda p: (p.arrival_time, p.pid))

        pid_map      = {p.pid: p for p in procs}
        ready_queue  = deque()          # Queue of PIDs
        completed    = set()
        current_time = 0
        n            = len(procs)

        # Index to track next process to check for arrival
        arrival_idx  = 0

        def enqueue_arrived(up_to_time: int):
            """Add all processes that have arrived by up_to_time to the ready queue."""
            nonlocal arrival_idx
            while arrival_idx < n and procs[arrival_idx].arrival_time <= up_to_time:
                p = procs[arrival_idx]
                if p.pid not in completed:
                    ready_queue.append(p.pid)
                arrival_idx += 1

        # Seed the queue with processes arriving at time 0
        enqueue_arrived(0)

        # If nothing arrived at 0, jump clock to first arrival
        if not ready_queue:
            current_time = procs[0].arrival_time
            enqueue_arrived(current_time)

        while len(completed) < n:

            if not ready_queue:
                # CPU idle — find next arrival and jump
                next_arr = min(
                    p.arrival_time for p in procs if p.pid not in completed
                )
                current_time = next_arr
                enqueue_arrived(current_time)
                continue

            # Dequeue next process
            pid     = ready_queue.popleft()
            process = pid_map[pid]

            # Record first response
            if process.start_time == -1:
                process.start_time    = current_time
                process.response_time = current_time - process.arrival_time

            # How long does this process actually run this turn?
            run_time   = min(self.time_quantum, process.remaining_time)
            block_start = current_time

            # Advance clock tick-by-tick to correctly catch new arrivals mid-quantum
            # (Optimised: jump the whole run_time, then add arrivals)
            current_time          += run_time
            process.remaining_time -= run_time

            # Record this execution block for the Gantt chart
            process.gantt_blocks.append((block_start, current_time))

            # Enqueue any processes that arrived during this execution window
            enqueue_arrived(current_time)

            if process.remaining_time == 0:
                # Process finished
                process.completion_time = current_time
                process.calculate_times()
                completed.add(pid)
            else:
                # Process preempted — goes to the back of the queue
                # New arrivals (added above) are already ahead — correct behaviour
                ready_queue.append(pid)

        return procs
