# OS Simulator

A small Python desktop app for the **Operating System project**. It uses Tkinter library for creating the user interface and has three main sections.

## Features

- **CPU Scheduling:** FCFS, SJF non-preemptive, SJF preemptive, and Round Robin. Shows process arrival time, burst time, finish time, waiting time, turnaround time, averages, and a Gantt chart.
- **Memory Allocation:** First Fit, Best Fit, and Worst Fit. Shows process allocation and remaining block sizes.
- **Page Replacement:** FIFO, Optimal, and LRU. Shows page faults, hits, miss ratio, hit ratio, and a step-by-step table.

## Requirements

- Python 3.10 or newer
- Tkinter
- **No extra pip packages are needed**. `requirements.txt` is included for setup consistency.

On Windows, install Python from https://www.python.org/downloads/. During setup, enable **Add Python to PATH**.

On Ubuntu or Linux Mint, install Python and Tkinter if they are not already installed:

```bash
sudo apt install python3 python3-venv python3-tk
```

On Fedora:

```bash
sudo dnf install python3 python3-tkinter
```

## Quick start

The run scripts create `.venv` if it does not exist, install the packages listed in `requirements.txt`, and start the app. The setup only needs to be done once. Later runs reuse the same environment.

### Windows

Double-click `run.bat`, or open a terminal in this folder and run:

```bat
run.bat
```

You can also run the cross-platform Python script directly:

```bat
py -3 run.py
```

### Linux

Open a terminal in this folder and run:

```bash
chmod +x run.sh
./run.sh
```

Or run the Python script directly:

```bash
python3 run.py
```

## Create and activate the virtual environment manually

If you prefer to set up the environment yourself, open a terminal in this folder.

### Windows Command Prompt

```bat
py -3 -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python app.py
```

### Windows PowerShell

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, you can skip activation and use the environment's Python directly:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

When you finish, leave the virtual environment with:

```bash
deactivate
```

## Input format

Enter numbers separated by commas. For CPU scheduling, the arrival and burst lists must have the same number of values. Each list position represents one process, starting with P1. Use zero for a process arrival time when it arrives at the start. Burst times, memory sizes, frame count, and Round Robin quantum must be greater than zero.

## Sample inputs to use

- CPU arrival times: `0, 1, 2, 3`
- CPU burst times: `5, 3, 8, 2`
- Round Robin quantum: `2`
- Memory blocks: `100, 500, 200, 300, 600`
- Process sizes: `212, 417, 112, 426`
- Page reference string: `7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2`
- Frame count: `3`

## Group members

| Student | Student ID |
| --- | --- |
| Abdulaziz Alhuzami | 202300716 |
| Asmatullah Baryali | 202300331 |
| Mohammed Alkhulaiteet | 202300206 |
| Yaseen Waqar | 202300623 |

## License

This project is released under the MIT License. See `LICENSE`.
