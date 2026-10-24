"""OS Simulator for the Principles of Operating System project."""

import tkinter as tk
from tkinter import ttk, messagebox
from collections import deque

APP_TITLE = "OS Simulator"


def parse_numbers(value, label, allow_zero=True):
    try:
        values = [int(part.strip()) for part in value.replace(";", ",").split(",") if part.strip()]
    except ValueError:
        raise ValueError(f"Enter whole numbers for {label}, separated by commas.")
    if not values:
        raise ValueError(f"Enter at least one value for {label}.")
    if any(n < 0 if allow_zero else n <= 0 for n in values):
        rule = "zero or greater" if allow_zero else "greater than zero"
        raise ValueError(f"Values for {label} must be {rule}.")
    return values


def schedule(processes, algorithm, quantum=1):
    """Return per-process results and a list of (label, start, end) chart segments."""
    items = {p["id"]: dict(p, remaining=p["burst"], completion=0, first_start=None) for p in processes}
    time = 0
    chart = []

    def add_segment(pid, start, end):
        if end <= start:
            return
        label = f"P{pid}" if pid is not None else "Idle"
        if chart and chart[-1][0] == label and chart[-1][2] == start:
            chart[-1] = (label, chart[-1][1], end)
        else:
            chart.append((label, start, end))

    if algorithm in ("FCFS", "SJF (Non-preemptive)"):
        pending = sorted(processes, key=lambda p: (p["arrival"], p["id"]))
        done = set()
        while len(done) < len(pending):
            ready = [p for p in pending if p["id"] not in done and p["arrival"] <= time]
            if not ready:
                next_arrival = min(p["arrival"] for p in pending if p["id"] not in done)
                add_segment(None, time, next_arrival)
                time = next_arrival
                continue
            if algorithm == "FCFS":
                p = min(ready, key=lambda x: (x["arrival"], x["id"]))
            else:
                p = min(ready, key=lambda x: (x["burst"], x["arrival"], x["id"]))
            start = time
            items[p["id"]]["first_start"] = start
            time += p["burst"]
            items[p["id"]]["completion"] = time
            add_segment(p["id"], start, time)
            done.add(p["id"])
    elif algorithm == "SJF (Preemptive)":
        while any(p["remaining"] > 0 for p in items.values()):
            ready = [p for p in items.values() if p["arrival"] <= time and p["remaining"] > 0]
            if not ready:
                next_arrival = min(p["arrival"] for p in items.values() if p["remaining"] > 0)
                add_segment(None, time, next_arrival)
                time = next_arrival
                continue
            p = min(ready, key=lambda x: (x["remaining"], x["arrival"], x["id"]))
            if p["first_start"] is None:
                p["first_start"] = time
            start = time
            time += 1
            p["remaining"] -= 1
            add_segment(p["id"], start, time)
            if p["remaining"] == 0:
                p["completion"] = time
    elif algorithm == "Round Robin":
        pending = sorted(processes, key=lambda p: (p["arrival"], p["id"]))
        ready = deque()
        index = 0
        while any(p["remaining"] > 0 for p in items.values()):
            while index < len(pending) and pending[index]["arrival"] <= time:
                ready.append(pending[index]["id"])
                index += 1
            if not ready:
                if index < len(pending):
                    next_time = pending[index]["arrival"]
                    add_segment(None, time, next_time)
                    time = next_time
                    continue
                break
            pid = ready.popleft()
            p = items[pid]
            if p["remaining"] <= 0:
                continue
            if p["first_start"] is None:
                p["first_start"] = time
            start = time
            run_for = min(quantum, p["remaining"])
            time += run_for
            p["remaining"] -= run_for
            add_segment(pid, start, time)
            while index < len(pending) and pending[index]["arrival"] <= time:
                ready.append(pending[index]["id"])
                index += 1
            if p["remaining"] > 0:
                ready.append(pid)
            else:
                p["completion"] = time
    else:
        raise ValueError("Choose a supported scheduling algorithm.")

    results = []
    for p in sorted(items.values(), key=lambda x: x["id"]):
        turnaround = p["completion"] - p["arrival"]
        waiting = turnaround - p["burst"]
        results.append({"id": p["id"], "arrival": p["arrival"], "burst": p["burst"],
                        "completion": p["completion"], "waiting": waiting, "turnaround": turnaround})
    return results, chart


def allocate_memory(blocks, processes, method):
    remaining = list(blocks)
    results = []
    for index, size in enumerate(processes, 1):
        candidates = [i for i, block in enumerate(remaining) if block >= size]
        chosen = None
        if candidates:
            if method == "First Fit":
                chosen = candidates[0]
            elif method == "Best Fit":
                chosen = min(candidates, key=lambda i: remaining[i])
            else:
                chosen = max(candidates, key=lambda i: remaining[i])
        if chosen is None:
            results.append((f"P{index}", size, "Not allocated", "-"))
        else:
            block_before = remaining[chosen]
            remaining[chosen] -= size
            results.append((f"P{index}", size, f"Block {chosen + 1}", block_before))
    return results, remaining


def page_replacement(reference, frame_count, algorithm):
    frames = []
    faults = 0
    hits = 0
    history = []
    last_used = {}
    for step, page in enumerate(reference):
        hit = page in frames
        if hit:
            hits += 1
        else:
            faults += 1
            if len(frames) < frame_count:
                frames.append(page)
            elif algorithm == "FIFO":
                frames.pop(0)
                frames.append(page)
            elif algorithm == "LRU":
                victim = min(frames, key=lambda item: last_used.get(item, -1))
                frames[frames.index(victim)] = page
            elif algorithm == "Optimal":
                future = reference[step + 1:]
                def next_use(item):
                    return future.index(item) if item in future else float("inf")
                victim = max(frames, key=next_use)
                frames[frames.index(victim)] = page
        last_used[page] = step
        history.append((page, list(frames), "Hit" if hit else "Fault"))
    total = len(reference)
    return {"faults": faults, "hits": hits, "miss_ratio": faults / total if total else 0,
            "hit_ratio": hits / total if total else 0, "history": history}


class OSSimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("980x700")
        self.minsize(780, 580)
        self.configure(bg="#f4f5f7")
        self._setup_style()
        self._build_shell()
        self.show_cpu()

    def _setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#f4f5f7")
        style.configure("TLabel", background="#f4f5f7", foreground="#20242b", font=("Arial", 10))
        style.configure("Title.TLabel", font=("Arial", 19, "bold"), foreground="#15191f")
        style.configure("Sub.TLabel", font=("Arial", 10), foreground="#606875")
        style.configure("TButton", font=("Arial", 10), padding=(12, 8))
        style.configure("Nav.TButton", font=("Arial", 10, "bold"), padding=(10, 12))
        style.configure("Treeview", rowheight=27, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    def _build_shell(self):
        header = ttk.Frame(self, padding=(22, 18, 22, 12))
        header.pack(fill="x")
        ttk.Label(header, text="OS Simulator", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="CPU scheduling, memory allocation, and page replacement", style="Sub.TLabel").pack(anchor="w", pady=(4, 0))
        nav = ttk.Frame(self, padding=(22, 0, 22, 12))
        nav.pack(fill="x")
        ttk.Button(nav, text="CPU Scheduling", style="Nav.TButton", command=self.show_cpu).pack(side="left", padx=(0, 8))
        ttk.Button(nav, text="Memory Allocation", style="Nav.TButton", command=self.show_memory).pack(side="left", padx=8)
        ttk.Button(nav, text="Page Replacement", style="Nav.TButton", command=self.show_pages).pack(side="left", padx=8)
        self.content = ttk.Frame(self, padding=(22, 8, 22, 22))
        self.content.pack(fill="both", expand=True)

    def clear_content(self):
        for child in self.content.winfo_children():
            child.destroy()

    def section_title(self, title, description):
        ttk.Label(self.content, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.content, text=description, style="Sub.TLabel", wraplength=850).pack(anchor="w", pady=(4, 14))

    def make_entry(self, parent, label, default, width=25):
        box = ttk.Frame(parent)
        box.pack(side="left", padx=(0, 14), anchor="n")
        ttk.Label(box, text=label).pack(anchor="w", pady=(0, 5))
        entry = ttk.Entry(box, width=width)
        entry.insert(0, default)
        entry.pack(anchor="w")
        return entry

    def make_table(self, parent, columns, headings, height=7):
        wrap = ttk.Frame(parent)
        wrap.pack(fill="both", expand=True, pady=(10, 0))
        tree = ttk.Treeview(wrap, columns=columns, show="headings", height=height)
        for col, heading in zip(columns, headings):
            tree.heading(col, text=heading)
            tree.column(col, width=max(85, int(800 / len(columns))), anchor="center")
        scroll = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return tree

    def show_cpu(self):
        self.clear_content()
        self.section_title("CPU Scheduling", "Enter process arrival and burst times, then run one scheduling method.")
        form = ttk.Frame(self.content)
        form.pack(fill="x")
        self.cpu_arrivals = self.make_entry(form, "Arrival times", "0, 1, 2, 3", 23)
        self.cpu_bursts = self.make_entry(form, "Burst times", "5, 3, 8, 2", 23)
        opts = ttk.Frame(self.content)
        opts.pack(fill="x", pady=(12, 0))
        ttk.Label(opts, text="Algorithm").pack(side="left", padx=(0, 8))
        self.cpu_algo = ttk.Combobox(opts, state="readonly", width=25, values=["FCFS", "SJF (Non-preemptive)", "SJF (Preemptive)", "Round Robin"])
        self.cpu_algo.set("FCFS")
        self.cpu_algo.pack(side="left")
        ttk.Label(opts, text="Quantum").pack(side="left", padx=(16, 6))
        self.cpu_quantum = ttk.Entry(opts, width=7)
        self.cpu_quantum.insert(0, "2")
        self.cpu_quantum.pack(side="left")
        ttk.Button(opts, text="Run", command=self.run_cpu).pack(side="left", padx=14)
        self.cpu_summary = ttk.Label(self.content, text="", font=("Arial", 10, "bold"))
        self.cpu_summary.pack(anchor="w", pady=(14, 0))
        self.cpu_table = self.make_table(self.content, ("pid", "arrival", "burst", "completion", "waiting", "turnaround"), ("Process", "Arrival", "Burst", "Finish", "Waiting", "Turnaround"), 6)
        self.cpu_chart = ttk.Label(self.content, text="Gantt chart will appear here.", wraplength=900, font=("Arial", 10))
        self.cpu_chart.pack(anchor="w", pady=(12, 0))
        self.run_cpu()

    def run_cpu(self):
        try:
            arrivals = parse_numbers(self.cpu_arrivals.get(), "arrival times")
            bursts = parse_numbers(self.cpu_bursts.get(), "burst times", allow_zero=False)
            if len(arrivals) != len(bursts):
                raise ValueError("Arrival and burst times must have the same number of values.")
            processes = [{"id": i + 1, "arrival": arrivals[i], "burst": bursts[i]} for i in range(len(arrivals))]
            quantum = int(self.cpu_quantum.get())
            if quantum <= 0:
                raise ValueError("Quantum must be greater than zero.")
            algo = self.cpu_algo.get()
            results, chart = schedule(processes, algo, quantum)
            for item in self.cpu_table.get_children():
                self.cpu_table.delete(item)
            for r in results:
                self.cpu_table.insert("", "end", values=(f"P{r['id']}", r["arrival"], r["burst"], r["completion"], r["waiting"], r["turnaround"]))
            avg_wait = sum(r["waiting"] for r in results) / len(results)
            avg_turn = sum(r["turnaround"] for r in results) / len(results)
            self.cpu_summary.config(text=f"{algo}    Average waiting time: {avg_wait:.2f}    Average turnaround time: {avg_turn:.2f}")
            parts = ["Gantt chart:"]
            parts.append("  ".join(f"{label} [{start}-{end}]" for label, start, end in chart))
            self.cpu_chart.config(text="\n".join(parts))
        except (ValueError, tk.TclError) as exc:
            messagebox.showerror("Input error", str(exc), parent=self)

    def show_memory(self):
        self.clear_content()
        self.section_title("Contiguous Memory Allocation", "Enter memory block sizes and process sizes, separated by commas.")
        form = ttk.Frame(self.content)
        form.pack(fill="x")
        self.mem_blocks = self.make_entry(form, "Memory blocks", "100, 500, 200, 300, 600", 30)
        self.mem_processes = self.make_entry(form, "Process sizes", "212, 417, 112, 426", 28)
        row = ttk.Frame(self.content)
        row.pack(fill="x", pady=(12, 0))
        ttk.Label(row, text="Method").pack(side="left", padx=(0, 8))
        self.mem_method = ttk.Combobox(row, state="readonly", width=18, values=["First Fit", "Best Fit", "Worst Fit"])
        self.mem_method.set("First Fit")
        self.mem_method.pack(side="left")
        ttk.Button(row, text="Run", command=self.run_memory).pack(side="left", padx=12)
        self.mem_table = self.make_table(self.content, ("process", "size", "allocation", "block_size"), ("Process", "Size", "Allocated to", "Block size before allocation"), 8)
        self.mem_summary = ttk.Label(self.content, text="", font=("Arial", 10, "bold"))
        self.mem_summary.pack(anchor="w", pady=(12, 0))
        self.run_memory()

    def run_memory(self):
        try:
            blocks = parse_numbers(self.mem_blocks.get(), "memory blocks", allow_zero=False)
            processes = parse_numbers(self.mem_processes.get(), "process sizes", allow_zero=False)
            rows, remaining = allocate_memory(blocks, processes, self.mem_method.get())
            for item in self.mem_table.get_children():
                self.mem_table.delete(item)
            for row in rows:
                self.mem_table.insert("", "end", values=row)
            allocated = sum(row[2] != "Not allocated" for row in rows)
            self.mem_summary.config(text=f"Allocated: {allocated} of {len(processes)} processes    Remaining block space: {', '.join(map(str, remaining))}")
        except ValueError as exc:
            messagebox.showerror("Input error", str(exc), parent=self)

    def show_pages(self):
        self.clear_content()
        self.section_title("Page Replacement", "Enter a reference string and frame count. The app compares FIFO, Optimal, and LRU.")
        form = ttk.Frame(self.content)
        form.pack(fill="x")
        self.page_refs = self.make_entry(form, "Reference string", "7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2", 47)
        self.page_frames = self.make_entry(form, "Frame count", "3", 12)
        ttk.Button(form, text="Run all", command=self.run_pages).pack(side="left", padx=(0, 10), pady=(20, 0))
        self.page_table = self.make_table(self.content, ("algorithm", "faults", "hits", "miss_ratio", "hit_ratio"), ("Algorithm", "Page faults", "Hits", "Miss ratio", "Hit ratio"), 4)
        ttk.Label(self.content, text="Page-by-page result", font=("Arial", 11, "bold")).pack(anchor="w", pady=(16, 4))
        self.page_detail = self.make_table(self.content, ("step", "page", "frames", "result"), ("Step", "Page", "Frames", "Result"), 8)
        self.run_pages()

    def run_pages(self):
        try:
            reference = parse_numbers(self.page_refs.get(), "reference string")
            frame_count = int(self.page_frames.get())
            if frame_count <= 0:
                raise ValueError("Frame count must be greater than zero.")
            outcomes = {name: page_replacement(reference, frame_count, name) for name in ("FIFO", "Optimal", "LRU")}
            for item in self.page_table.get_children():
                self.page_table.delete(item)
            for name, result in outcomes.items():
                self.page_table.insert("", "end", values=(name, result["faults"], result["hits"], f"{result['miss_ratio']:.2%}", f"{result['hit_ratio']:.2%}"))
            for item in self.page_detail.get_children():
                self.page_detail.delete(item)
            result = outcomes["FIFO"]
            for step, (page, frames, status) in enumerate(result["history"], 1):
                self.page_detail.insert("", "end", values=(step, page, "[" + ", ".join(map(str, frames)) + "]", status))
        except ValueError as exc:
            messagebox.showerror("Input error", str(exc), parent=self)


if __name__ == "__main__":
    app = OSSimulator()
    app.mainloop()
