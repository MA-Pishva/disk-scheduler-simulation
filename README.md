# Disk I/O Scheduler Simulation (Elevator / LOOK vs. FCFS)

A Python discrete-event simulation and Monte Carlo benchmarking tool comparing **Elevator (LOOK/SCAN)** and **First-Come, First-Served (FCFS)** disk scheduling algorithms under a realistic physical hard-drive timing model (modeled on the **Megatron 747** storage architecture).

## Physical Disk Timing Model

Every disk I/O request incurs three physical latency components:

1. **Seek Time ($T_{\text{seek}}$):**
   - If the read/write head moves across $\Delta c = |c_{\text{target}} - c_{\text{current}}| > 0$ cylinders:
     $$T_{\text{seek}} = T_{\text{startup/stop}} + \frac{\Delta c}{R_{\text{traverse}}}$$
     where $T_{\text{startup/stop}} = 1.0\text{ ms}$ (`HEAD_DELAY`) and $R_{\text{traverse}} = 4000\text{ cylinders/ms}$ (`TRACK_TRAVERSED_IN_ONE_MS`).
   - If $\Delta c = 0$, $T_{\text{seek}} = 0\text{ ms}$.
2. **Rotational Latency ($T_{\text{rot}}$):** Default $4.17\text{ ms}$ (randomized in $[2.0, 8.0]\text{ ms}$ during Monte Carlo runs).
3. **Transfer Time ($T_{\text{xfer}}$):** Default $0.13\text{ ms}$ (randomized in $[0.01, 0.20]\text{ ms}$ during Monte Carlo runs).

## Features

- **Arrival-Aware Elevator (LOOK) Scheduler (`elevator`):**
  - Uses binary search (`requested_received`) to filter requests that have arrived by the current simulation clock (`elapsed_time`).
  - Sweeps in the active head direction (`move = 1` upward, `move = 0` downward) and dynamically intercepts requests arriving along the head's path (`midway_requests`, `response_midway_requested`) before reversing direction.
- **FCFS Baseline Scheduler (`fcfs`):**
  - Services I/O requests strictly in arrival order, advancing the simulation clock during idle intervals.
- **Interactive & Monte Carlo Benchmark Modes (`menu`):**
  - **Option 1 — Manual Input:** Accepts an initial head cylinder and `(cylinder, arrival_time)` pairs, printing a side-by-side completion-time table for Elevator vs. FCFS.
  - **Option 2 — Random Workload Generator:** Simulates $N$ randomized 100-request workloads across cylinders $[0, 100{,}000]$ and plots average per-request completion time and total workload makespan comparisons using `matplotlib`.

## Project Structure

```text
disk-scheduler-simulation/
├── .gitignore
├── requirements.txt
├── README.md
├── sample_input.txt
└── src/
    └── main.py
```

## Getting Started

### Prerequisites
- Python 3.8+
- `matplotlib`

### Installation & Run
```bash
pip install -r requirements.txt

# Run interactively
python src/main.py

# Or run with the built-in Megatron 747 sample workload
python src/main.py < sample_input.txt
```

### Sample Benchmark Output (`sample_input.txt`)
With initial head at cylinder `8000`, `rotational_latency = 4.17 ms`, and `transfer_time = 0.13 ms`:

| Request Order (Elevator) | Elevator Completion (ms) | Request Order (FCFS) | FCFS Completion (ms) |
| :---: | :---: | :---: | :---: |
| `8000` | `4.3` | `8000` | `4.3` |
| `24000` | `13.6` | `24000` | `13.6` |
| `56000` | `26.9` | `56000` | `26.9` |
| `64000` | `34.2` | `16000` | `42.2` |
| `40000` | `45.5` | `64000` | `59.5` |
| `16000` | `56.8` | `40000` | `70.8` |
