<div align="center">

# ⚡ KernelFlow
### CPU Scheduling Simulator

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-FF6B6B?style=for-the-badge)
![Matplotlib](https://img.shields.io/badge/Charts-Matplotlib-11557C?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-2ECC71?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-6C63FF?style=for-the-badge)

**An interactive desktop application for learning and visualizing CPU scheduling algorithms.**
Built with pure Python — no web framework, no database, no external UI library.

[Features](#-features) · [Algorithms](#-algorithms) · [Installation](#-installation) · [Usage](#-usage) · [Architecture](#-architecture) · [Screenshots](#-screenshots)

</div>

---

## 🎯 What is KernelFlow?

KernelFlow is a **professional desktop simulator** designed for Computer Science students, OS learners, and university instructors. It brings CPU scheduling algorithms to life through an interactive dark-themed GUI, animated Gantt charts, and real-time performance statistics.

Enter your processes, pick an algorithm, and watch the scheduler execute — step by step.

---

## ✨ Features

### Core Simulation
- **6 scheduling algorithms** out of the box, all producing correct results
- **Real-time metrics** — Waiting Time, Turnaround Time, Response Time, CPU Utilization, Throughput
- **Animated Gantt chart** — replay execution block by block at 500ms per step
- **Algorithm comparison** — run all algorithms simultaneously on the same process set

### User Interface
- **Professional dark theme** — deep purple/navy palette, fully consistent across all widgets
- **3-panel layout** — Input | Results + Gantt | Statistics, all resizable
- **Color-coded processes** — every process gets a unique color shared across tables, Gantt, and stats
- **Live input validation** — fields highlight red with specific error messages on bad input
- **Auto-incrementing PID** — no manual typing of P1, P2, P3…

### Educational Tools
- **Step-by-step Gantt replay** — watch the CPU allocate time slice by slice
- **Ready queue visualizer** — see which processes are waiting
- **Algorithm info card** — explains each algorithm's characteristics after every run
- **Comparison tab** — grouped bar chart + table with ★ marking the best performer

---

## 🧠 Algorithms

| Algorithm | Mode | Key Characteristic |
|---|---|---|
| **FCFS** | Non-preemptive | Arrival order. Simple. Convoy effect. |
| **SJF** | Non-preemptive | Shortest burst wins. Optimal avg WT. |
| **SJF (Preemptive)** | Preemptive (SRTF) | Shortest remaining time. Min possible avg WT. |
| **Round Robin** | Preemptive | Fixed quantum. Fair. Great for interactive systems. |
| **Priority** | Non-preemptive | Lower number = higher priority. May starve. |
| **Priority (Preemptive)** | Preemptive | Immediately preempts on higher-priority arrival. |

### Example — 3 Processes

| Process | Arrival | Burst | Priority |
|---------|---------|-------|----------|
| P1 | 0 | 5 | 2 |
| P2 | 1 | 3 | 1 |
| P3 | 2 | 8 | 3 |

**FCFS result:**
```
| P1          | P2      | P3                      |
0             5         8                         16
Avg WT = 3.33   CPU = 100%
```

**Round Robin (q=2) result:**
```
| P1 | P2 | P3 | P1 | P2 | P3 | P1 | P3          |
0    2    4    6    8   9   11  12  13            16
Avg WT = 6.0   CPU = 100%
```

---

## 💻 Installation

### Prerequisites
- Python **3.8 or higher**
- Tkinter — bundled with standard Python on Windows and macOS
  - Linux: `sudo apt install python3-tk`

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/KernelFlow.git
cd KernelFlow

# 2. (Optional) Create a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the application
python main.py
```

### Dependencies

```
matplotlib >= 3.7.0   # Gantt chart and comparison bar chart
numpy      >= 1.24.0  # Required by matplotlib
tkinter                # Bundled with Python (no install needed)
```

---

## 🚀 Usage

### Step 1 — Add Processes
Fill in the left panel:
- **Process ID** — unique name (e.g. `P1`, `JobA`)
- **Arrival Time** — when the process enters the ready queue (≥ 0)
- **Burst Time** — CPU time required (≥ 1)
- **Priority** — lower number = higher priority (0–99)

Click **＋ Add Process** or press **Enter**.

### Step 2 — Select Algorithm
Choose from the dropdown:
- `FCFS` / `SJF` / `SJF (Preemptive)` / `Round Robin` / `Priority` / `Priority (Preemptive)`
- For **Round Robin**, set the **Time Quantum** (appears automatically).

### Step 3 — Run Simulation
Click **▶ Run Simulation**.

Results appear instantly across three areas:
- **Results Table** — per-process CT, WT, TAT, RT
- **Gantt Chart** — color-coded execution timeline
- **Statistics Panel** — aggregate metrics with color-coded ratings

### Step 4 — Explore
- Click **▶ Replay** on the Gantt chart for step-by-step animation
- Switch to the **⚖ Compare All** tab to benchmark all algorithms at once
- Click **↺ Reset** to clear results and try a different algorithm on the same processes
- Click **Clear All** to start fresh

---

## 🏗 Architecture

```
KernelFlow/
│
├── main.py                        # Entry point
│
├── algorithms/                    # Plugin-pattern algorithm layer
│   ├── base_algorithm.py          # Abstract base (BaseAlgorithm)
│   ├── fcfs.py                    # First Come First Serve
│   ├── sjf.py                     # Shortest Job First (both modes)
│   ├── round_robin.py             # Round Robin
│   └── priority.py                # Priority Scheduling (both modes)
│
├── models/
│   └── process.py                 # Process dataclass (shared data object)
│
├── ui/
│   ├── theme.py                   # All colors, fonts, styles (single source)
│   ├── main_window.py             # Root window + layout controller
│   ├── input_panel.py             # Left panel — process entry form
│   ├── results_panel.py           # Center — process + results tables
│   ├── gantt_chart.py             # Matplotlib Gantt + comparison chart
│   └── stats_panel.py             # Right panel — statistics cards
│
└── utils/
    ├── scheduler.py               # Orchestrator + ALGORITHM_REGISTRY
    ├── metrics.py                 # Aggregate statistics calculation
    └── validators.py              # Input validation (pure functions)
```

### Design Principles

**Plugin Pattern for Algorithms**
Every algorithm subclasses `BaseAlgorithm` and implements one method: `run()`.
Adding a new algorithm requires two changes only:
1. Create `algorithms/my_algo.py`
2. Add one line to `ALGORITHM_REGISTRY` in `utils/scheduler.py`

**Single Source of Truth for Design**
`ui/theme.py` holds every color, font, and spacing constant.
No hex color string appears twice in the codebase.

**Separation of Concerns**
- Algorithm files have zero Tkinter imports — fully unit-testable
- `metrics.py` and `validators.py` are pure functions
- `MainWindow` coordinates panels via callbacks — panels never reference each other

**Shared Data Object**
The `Process` dataclass travels through every layer unchanged.
Input fields are set once; computed fields are populated by the algorithm.
No data conversion or re-mapping between layers.

---

## 📊 Metrics Explained

| Metric | Formula | Meaning |
|--------|---------|---------|
| **Completion Time (CT)** | Set by algorithm | When the process finished |
| **Turnaround Time (TAT)** | CT − Arrival | Total time from arrival to finish |
| **Waiting Time (WT)** | TAT − Burst | Time spent waiting in the queue |
| **Response Time (RT)** | First CPU − Arrival | Time until first CPU response |
| **CPU Utilization** | Burst Sum ÷ Makespan × 100 | % of time CPU was busy |
| **Throughput** | N ÷ Makespan | Processes completed per time unit |

---

## 📸 Screenshots

> *Run the application and use your OS screenshot tool to capture these views.*

| View | Description |
|------|-------------|
| `screenshots/main_fcfs.png` | FCFS simulation with Gantt chart |
| `screenshots/round_robin.png` | Round Robin with animated Gantt |
| `screenshots/comparison.png` | Algorithm comparison bar chart |
| `screenshots/stats_panel.png` | Statistics cards with color ratings |

---

## 🔬 Adding a New Algorithm

1. Create `algorithms/my_algorithm.py`:

```python
from algorithms.base_algorithm import BaseAlgorithm
from models.process import Process
from typing import List

class MyAlgorithm(BaseAlgorithm):
    name        = "My Algorithm"
    description = "One-line description shown in the UI."

    def run(self, processes: List[Process]) -> List[Process]:
        procs = self.prepare_processes(processes)  # deep copy + reset
        # ... your scheduling logic ...
        # Set for each process:
        #   p.start_time, p.completion_time, p.gantt_blocks
        #   then call p.calculate_times()
        return procs
```

2. Register it in `utils/scheduler.py`:

```python
from algorithms.my_algorithm import MyAlgorithm

ALGORITHM_REGISTRY = {
    ...
    "My Algorithm": MyAlgorithm(),   # ← add this one line
}

ALGORITHM_NAMES = [
    ...
    "My Algorithm",                  # ← and this one line
]
```

That's it. The new algorithm appears in the dropdown, runs in comparison mode,
and produces a Gantt chart automatically.

---

## 🎓 Learning Objectives

After using KernelFlow, students should be able to:

- **Explain** why FCFS causes the convoy effect with a concrete example
- **Demonstrate** that SJF gives optimal average waiting time (non-preemptive)
- **Calculate** WT, TAT, and RT by hand and verify against the simulator
- **Compare** algorithm trade-offs: fairness vs. efficiency vs. response time
- **Understand** why Round Robin quantum size matters (too small = overhead, too large ≈ FCFS)
- **Identify** when preemptive scheduling reduces response time at the cost of context switches

---

## 🛠 Development Notes

### Running Tests (manual)
```bash
# Algorithm correctness
python -c "
from models.process import create_process
from utils.scheduler import run_simulation
p = [create_process('P1',0,5,2), create_process('P2',1,3,1), create_process('P3',2,8,3)]
r = run_simulation(p, 'FCFS')
for proc in r.processes: print(proc)
"
```

### Platform Notes
| Platform | Tkinter | Notes |
|----------|---------|-------|
| Windows 10/11 | ✅ Bundled | DPI-awareness enabled automatically |
| macOS 12+ | ✅ Bundled | May need `brew install python-tk` |
| Ubuntu/Debian | ⚠ Separate | `sudo apt install python3-tk` |
| Arch Linux | ⚠ Separate | `sudo pacman -S tk` |

---

## 📄 License

MIT License — free to use, modify, and distribute.
See `LICENSE` for details.

---

## 👤 Author

Built as a portfolio project demonstrating:
- Object-oriented Python architecture
- Desktop GUI development with Tkinter
- Data visualization with Matplotlib
- Clean code, modular design, and extensibility

---

<div align="center">

**⚡ KernelFlow** — Making CPU Scheduling Visual

*If this project helped you understand OS scheduling, consider giving it a ⭐*

</div>
