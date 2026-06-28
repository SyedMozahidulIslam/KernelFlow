"""
algorithms package
==================
Exports all scheduling algorithm classes.
Import from here to avoid deep path references.
"""
from .base_algorithm import BaseAlgorithm
from .fcfs           import FCFS
from .sjf            import SJF
from .round_robin    import RoundRobin
from .priority       import Priority

__all__ = ["BaseAlgorithm", "FCFS", "SJF", "RoundRobin", "Priority"]
