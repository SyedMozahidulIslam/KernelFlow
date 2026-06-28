"""
utils/validators.py
===================
All input validation logic for KernelFlow.

Design:
  - Pure functions: no Tkinter imports, no UI dependencies
  - Each function returns a ValidationResult (ok=True/False, message=str)
  - The UI layer calls these and displays the message if ok=False
  - Fully testable without launching a window
"""

from dataclasses import dataclass
from typing import List, Optional


# ─────────────────────────────────────────────
#  Result Container
# ─────────────────────────────────────────────

@dataclass
class ValidationResult:
    """
    Returned by every validator function.

    Attributes:
        ok      : True if input is valid, False otherwise
        message : Human-readable error message (empty string if ok=True)
        field   : Which field caused the error (empty string if ok=True)
    """
    ok:      bool
    message: str  = ""
    field:   str  = ""

    def __bool__(self) -> bool:
        """Allows `if validate_pid(...)` syntax."""
        return self.ok


# ─────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────

MAX_PROCESSES    = 20       # Maximum processes allowed in one simulation
MAX_BURST_TIME   = 1000     # Guard against absurdly long simulations
MAX_ARRIVAL_TIME = 1000
MAX_PRIORITY     = 99
MIN_QUANTUM      = 1
MAX_QUANTUM      = 100
MAX_PID_LENGTH   = 10


# ─────────────────────────────────────────────
#  Field-Level Validators
# ─────────────────────────────────────────────

def validate_pid(pid: str, existing_pids: List[str] = None) -> ValidationResult:
    """
    Validates a Process ID string.

    Rules:
        - Must not be empty or whitespace-only
        - Must not exceed MAX_PID_LENGTH characters
        - Must be unique among existing_pids (if provided)
        - Allowed characters: letters, digits, underscore, hyphen
    """
    pid = pid.strip()

    if not pid:
        return ValidationResult(ok=False, message="Process ID cannot be empty.", field="pid")

    if len(pid) > MAX_PID_LENGTH:
        return ValidationResult(
            ok=False,
            message=f"Process ID must be {MAX_PID_LENGTH} characters or fewer.",
            field="pid"
        )

    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
    if not all(c in allowed for c in pid):
        return ValidationResult(
            ok=False,
            message="Process ID may only contain letters, digits, '_', or '-'.",
            field="pid"
        )

    if existing_pids and pid in existing_pids:
        return ValidationResult(
            ok=False,
            message=f"Process ID '{pid}' already exists. Use a unique name.",
            field="pid"
        )

    return ValidationResult(ok=True)


def validate_arrival_time(value: str) -> ValidationResult:
    """
    Validates the arrival time input string.

    Rules:
        - Must be a non-negative integer
        - Must not exceed MAX_ARRIVAL_TIME
    """
    value = value.strip()

    if not value:
        return ValidationResult(ok=False, message="Arrival time cannot be empty.", field="arrival")

    if not value.lstrip('0').isdigit() and value != '0':
        # Handle edge case: "0" would fail lstrip check
        if not value.isdigit():
            return ValidationResult(
                ok=False,
                message="Arrival time must be a whole number (e.g. 0, 2, 5).",
                field="arrival"
            )

    try:
        val = int(value)
    except ValueError:
        return ValidationResult(
            ok=False,
            message="Arrival time must be a whole number (e.g. 0, 2, 5).",
            field="arrival"
        )

    if val < 0:
        return ValidationResult(
            ok=False,
            message="Arrival time cannot be negative.",
            field="arrival"
        )

    if val > MAX_ARRIVAL_TIME:
        return ValidationResult(
            ok=False,
            message=f"Arrival time cannot exceed {MAX_ARRIVAL_TIME}.",
            field="arrival"
        )

    return ValidationResult(ok=True)


def validate_burst_time(value: str) -> ValidationResult:
    """
    Validates the burst time input string.

    Rules:
        - Must be a positive integer (strictly > 0)
        - Must not exceed MAX_BURST_TIME
    """
    value = value.strip()

    if not value:
        return ValidationResult(ok=False, message="Burst time cannot be empty.", field="burst")

    try:
        val = int(value)
    except ValueError:
        return ValidationResult(
            ok=False,
            message="Burst time must be a whole number (e.g. 1, 5, 10).",
            field="burst"
        )

    if val <= 0:
        return ValidationResult(
            ok=False,
            message="Burst time must be at least 1.",
            field="burst"
        )

    if val > MAX_BURST_TIME:
        return ValidationResult(
            ok=False,
            message=f"Burst time cannot exceed {MAX_BURST_TIME}.",
            field="burst"
        )

    return ValidationResult(ok=True)


def validate_priority(value: str) -> ValidationResult:
    """
    Validates the priority input string.

    Rules:
        - Must be an integer (can be 0)
        - Must be between 0 and MAX_PRIORITY (inclusive)
        - Lower number = higher priority in the scheduler
    """
    value = value.strip()

    if not value:
        return ValidationResult(ok=False, message="Priority cannot be empty.", field="priority")

    try:
        val = int(value)
    except ValueError:
        return ValidationResult(
            ok=False,
            message="Priority must be a whole number (e.g. 0, 1, 2).",
            field="priority"
        )

    if val < 0:
        return ValidationResult(
            ok=False,
            message="Priority cannot be negative.",
            field="priority"
        )

    if val > MAX_PRIORITY:
        return ValidationResult(
            ok=False,
            message=f"Priority cannot exceed {MAX_PRIORITY}.",
            field="priority"
        )

    return ValidationResult(ok=True)


def validate_time_quantum(value: str) -> ValidationResult:
    """
    Validates the Round Robin time quantum input.

    Rules:
        - Must be a positive integer
        - Must be between MIN_QUANTUM and MAX_QUANTUM (inclusive)
    """
    value = value.strip()

    if not value:
        return ValidationResult(
            ok=False,
            message="Time quantum cannot be empty for Round Robin.",
            field="quantum"
        )

    try:
        val = int(value)
    except ValueError:
        return ValidationResult(
            ok=False,
            message="Time quantum must be a whole number (e.g. 2, 4).",
            field="quantum"
        )

    if val < MIN_QUANTUM:
        return ValidationResult(
            ok=False,
            message=f"Time quantum must be at least {MIN_QUANTUM}.",
            field="quantum"
        )

    if val > MAX_QUANTUM:
        return ValidationResult(
            ok=False,
            message=f"Time quantum cannot exceed {MAX_QUANTUM}.",
            field="quantum"
        )

    return ValidationResult(ok=True)


# ─────────────────────────────────────────────
#  Form-Level Validator (validates all fields together)
# ─────────────────────────────────────────────

def validate_process_form(
    pid:          str,
    arrival_time: str,
    burst_time:   str,
    priority:     str,
    existing_pids: List[str] = None
) -> ValidationResult:
    """
    Validates all four process input fields together.
    Returns the first error found, or ok=True if all pass.

    Args:
        pid           : Raw PID input string from the UI
        arrival_time  : Raw arrival time string
        burst_time    : Raw burst time string
        priority      : Raw priority string
        existing_pids : List of PIDs already added (for duplicate check)

    Returns:
        ValidationResult — first error encountered, or ok=True
    """
    checks = [
        validate_pid(pid, existing_pids),
        validate_arrival_time(arrival_time),
        validate_burst_time(burst_time),
        validate_priority(priority),
    ]
    for result in checks:
        if not result.ok:
            return result

    return ValidationResult(ok=True)


# ─────────────────────────────────────────────
#  Simulation-Level Validators
# ─────────────────────────────────────────────

def validate_process_list(processes: list) -> ValidationResult:
    """
    Validates the full list of processes before running the simulation.

    Rules:
        - Must have at least 1 process
        - Must not exceed MAX_PROCESSES
        - All PIDs must be unique (double-check after individual additions)
    """
    if not processes:
        return ValidationResult(
            ok=False,
            message="Add at least one process before running the simulation.",
            field="process_list"
        )

    if len(processes) > MAX_PROCESSES:
        return ValidationResult(
            ok=False,
            message=f"Maximum {MAX_PROCESSES} processes allowed per simulation.",
            field="process_list"
        )

    pids = [p.pid for p in processes]
    if len(pids) != len(set(pids)):
        duplicates = [pid for pid in pids if pids.count(pid) > 1]
        return ValidationResult(
            ok=False,
            message=f"Duplicate Process IDs found: {set(duplicates)}. All PIDs must be unique.",
            field="process_list"
        )

    return ValidationResult(ok=True)


def validate_algorithm_selection(algorithm_name: str, quantum_str: str = "") -> ValidationResult:
    """
    Validates the algorithm selection and associated parameters.

    Args:
        algorithm_name : The name string from the dropdown (e.g. "Round Robin")
        quantum_str    : Time quantum string (only checked for Round Robin)

    Returns:
        ValidationResult
    """
    valid_algorithms = {"FCFS", "SJF", "Round Robin", "Priority"}

    if not algorithm_name or algorithm_name not in valid_algorithms:
        return ValidationResult(
            ok=False,
            message=f"Please select a valid algorithm: {', '.join(sorted(valid_algorithms))}.",
            field="algorithm"
        )

    if algorithm_name == "Round Robin":
        return validate_time_quantum(quantum_str)

    return ValidationResult(ok=True)
