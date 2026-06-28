"""
utils/metrics.py
================
Pure calculation functions for aggregate simulation statistics.
No Tkinter, no UI — fully testable in isolation.

All functions accept a list of fully-computed Process objects
(i.e. after algorithm.run() has been called).
"""

from typing import List, Dict, Any
from models.process import Process


def compute_metrics(processes: List[Process]) -> Dict[str, Any]:
    """
    Compute all aggregate statistics from a completed simulation.

    Args:
        processes : List of Process objects with completion_time set.

    Returns:
        Dict with the following keys:
          avg_waiting_time    : float — mean waiting time across all processes
          avg_turnaround_time : float — mean turnaround time
          avg_response_time   : float — mean response time
          cpu_utilization     : float — percentage of time CPU was busy (0–100)
          throughput          : float — processes completed per unit time
          total_time          : int   — makespan (last completion - first arrival)
          idle_time           : int   — total time CPU spent idle
    """
    if not processes:
        return _empty_metrics()

    n = len(processes)

    # ── Aggregate timing fields ────────────────────────────
    total_wt  = sum(p.waiting_time    for p in processes if p.waiting_time    != -1)
    total_tat = sum(p.turnaround_time for p in processes if p.turnaround_time != -1)
    total_rt  = sum(p.response_time   for p in processes if p.response_time   != -1)

    avg_wt  = round(total_wt  / n, 2)
    avg_tat = round(total_tat / n, 2)
    avg_rt  = round(total_rt  / n, 2)

    # ── Makespan: first arrival → last completion ──────────
    first_arrival   = min(p.arrival_time    for p in processes)
    last_completion = max(p.completion_time for p in processes if p.completion_time != -1)
    total_time      = last_completion - first_arrival

    # ── CPU busy time = sum of all burst times ─────────────
    # (idle time = makespan - busy time)
    total_burst = sum(p.burst_time for p in processes)
    idle_time   = max(0, total_time - total_burst)

    # ── CPU Utilisation ────────────────────────────────────
    if total_time > 0:
        cpu_utilization = round((total_burst / total_time) * 100, 2)
    else:
        cpu_utilization = 100.0   # edge case: all processes arrive and finish instantly

    # ── Throughput: processes / total time ─────────────────
    if total_time > 0:
        throughput = round(n / total_time, 4)
    else:
        throughput = float(n)

    return {
        "avg_waiting_time":    avg_wt,
        "avg_turnaround_time": avg_tat,
        "avg_response_time":   avg_rt,
        "cpu_utilization":     cpu_utilization,
        "throughput":          throughput,
        "total_time":          total_time,
        "idle_time":           idle_time,
        "num_processes":       n,
    }


def _empty_metrics() -> Dict[str, Any]:
    """Returns zeroed metrics when no processes are provided."""
    return {
        "avg_waiting_time":    0.0,
        "avg_turnaround_time": 0.0,
        "avg_response_time":   0.0,
        "cpu_utilization":     0.0,
        "throughput":          0.0,
        "total_time":          0,
        "idle_time":           0,
        "num_processes":       0,
    }


def format_metrics_for_display(metrics: Dict[str, Any]) -> Dict[str, str]:
    """
    Converts raw metric values to display-ready strings for the stats panel.

    Returns:
        Dict with the same keys but human-readable string values.
    """
    return {
        "avg_waiting_time":    f"{metrics['avg_waiting_time']} units",
        "avg_turnaround_time": f"{metrics['avg_turnaround_time']} units",
        "avg_response_time":   f"{metrics['avg_response_time']} units",
        "cpu_utilization":     f"{metrics['cpu_utilization']}%",
        "throughput":          f"{metrics['throughput']} proc/unit",
        "total_time":          f"{metrics['total_time']} units",
        "idle_time":           f"{metrics['idle_time']} units",
        "num_processes":       str(metrics['num_processes']),
    }
