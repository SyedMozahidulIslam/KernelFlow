"""
utils/scheduler.py
==================
The Orchestrator — bridges the UI and the algorithm layer.

Responsibilities:
  1. Maintain ALGORITHM_REGISTRY (the only place algorithms are registered)
  2. Receive raw user inputs, instantiate the right algorithm, run it
  3. Return enriched Process objects + Gantt summary to the UI
  4. Produce a comparison run across ALL algorithms at once

Adding a new algorithm:
  1. Create algorithms/my_algo.py  (subclass BaseAlgorithm, implement run())
  2. Add one entry to ALGORITHM_REGISTRY below — nothing else changes
"""

from typing import List, Dict, Any, Optional
from copy import deepcopy

from algorithms.fcfs        import FCFS
from algorithms.sjf         import SJF
from algorithms.round_robin import RoundRobin
from algorithms.priority    import Priority
from algorithms.base_algorithm import BaseAlgorithm
from models.process         import Process
from utils.metrics          import compute_metrics


# ─────────────────────────────────────────────
#  Algorithm Registry
#  ↓ ADD NEW ALGORITHMS HERE (one line each) ↓
# ─────────────────────────────────────────────

def _build_registry() -> Dict[str, BaseAlgorithm]:
    """
    Returns a dict mapping display name → algorithm instance.
    Instances are created once and reused (they are stateless between runs).
    """
    return {
        "FCFS":                 FCFS(),
        "SJF":                  SJF(preemptive=False),
        "SJF (Preemptive)":     SJF(preemptive=True),
        "Round Robin":          RoundRobin(time_quantum=2),   # quantum set per-run
        "Priority":             Priority(preemptive=False),
        "Priority (Preemptive)": Priority(preemptive=True),
    }

ALGORITHM_REGISTRY = _build_registry()

# Names shown in the UI dropdown (ordered for display)
ALGORITHM_NAMES = [
    "FCFS",
    "SJF",
    "SJF (Preemptive)",
    "Round Robin",
    "Priority",
    "Priority (Preemptive)",
]


# ─────────────────────────────────────────────
#  Result Container
# ─────────────────────────────────────────────

class SimulationResult:
    """
    Encapsulates everything the UI needs after a simulation run.

    Attributes:
        algorithm_name : Name of the algorithm used
        processes      : List of Process objects with all fields computed
        gantt_blocks   : Chronological list of {"pid", "start", "end"} dicts
        metrics        : Dict of aggregate statistics (from metrics.py)
        time_quantum   : Quantum used (only relevant for Round Robin, else None)
    """

    def __init__(
        self,
        algorithm_name: str,
        processes:      List[Process],
        gantt_blocks:   List[dict],
        metrics:        Dict[str, Any],
        time_quantum:   Optional[int] = None,
    ):
        self.algorithm_name = algorithm_name
        self.processes      = processes
        self.gantt_blocks   = gantt_blocks
        self.metrics        = metrics
        self.time_quantum   = time_quantum

    def __repr__(self) -> str:
        return (
            f"SimulationResult(algo={self.algorithm_name!r}, "
            f"processes={len(self.processes)}, "
            f"avg_wt={self.metrics.get('avg_waiting_time', '?')})"
        )


# ─────────────────────────────────────────────
#  Core Run Function
# ─────────────────────────────────────────────

def run_simulation(
    processes:      List[Process],
    algorithm_name: str,
    time_quantum:   int = 2,
) -> SimulationResult:
    """
    Run the scheduling simulation for a single algorithm.

    Args:
        processes      : List of Process objects (input fields must be set)
        algorithm_name : Key from ALGORITHM_NAMES (e.g. "Round Robin")
        time_quantum   : Used only when algorithm_name == "Round Robin"

    Returns:
        SimulationResult with enriched processes, Gantt data, and metrics.

    Raises:
        ValueError : If algorithm_name is not in the registry.
        ValueError : If process list is empty.
    """
    if not processes:
        raise ValueError("Scheduler: cannot run simulation with empty process list.")

    if algorithm_name not in ALGORITHM_REGISTRY:
        available = ", ".join(ALGORITHM_NAMES)
        raise ValueError(
            f"Unknown algorithm: '{algorithm_name}'. "
            f"Available: {available}"
        )

    # For Round Robin, create a fresh instance with the user's quantum
    if algorithm_name == "Round Robin":
        algorithm = RoundRobin(time_quantum=time_quantum)
    else:
        algorithm = ALGORITHM_REGISTRY[algorithm_name]

    # Deep-copy processes so the originals stay clean in the UI process list
    input_copies = deepcopy(processes)

    # Execute the algorithm
    completed_procs = algorithm.run(input_copies)

    # Build the flat Gantt block list for the chart renderer
    gantt_blocks = algorithm.build_gantt_summary(completed_procs)

    # Compute aggregate statistics
    metrics = compute_metrics(completed_procs)

    return SimulationResult(
        algorithm_name = algorithm_name,
        processes      = completed_procs,
        gantt_blocks   = gantt_blocks,
        metrics        = metrics,
        time_quantum   = time_quantum if algorithm_name == "Round Robin" else None,
    )


# ─────────────────────────────────────────────
#  Comparison Run (all algorithms at once)
# ─────────────────────────────────────────────

def run_comparison(
    processes:    List[Process],
    time_quantum: int = 2,
) -> Dict[str, SimulationResult]:
    """
    Run ALL registered algorithms on the same process set and return results.
    Used by the Comparison tab in the UI.

    Args:
        processes    : Shared input process list
        time_quantum : Quantum for Round Robin

    Returns:
        Dict mapping algorithm_name → SimulationResult for each algorithm.
    """
    results = {}
    for name in ALGORITHM_NAMES:
        try:
            results[name] = run_simulation(processes, name, time_quantum)
        except Exception as e:
            # Log but don't crash — partial comparison is better than none
            print(f"[Scheduler] Warning: '{name}' failed during comparison: {e}")
    return results


# ─────────────────────────────────────────────
#  Utility: get quantum from a result
# ─────────────────────────────────────────────

def get_display_name(algorithm_name: str, time_quantum: int = 2) -> str:
    """Returns a display-ready name including quantum for Round Robin."""
    if algorithm_name == "Round Robin":
        return f"Round Robin (q={time_quantum})"
    return algorithm_name
