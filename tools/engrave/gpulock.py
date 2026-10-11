"""Cross-process GPU semaphore: at most N engrave jobs use the GPU at once (flock on slot files).

Several directors may launch engrave.py at the same time on the one RTX 3090. Each job grabs one
of N slot locks (default 2, env ENGRAVE_GPU_SLOTS) before touching CUDA and holds it until it
exits; the others wait (polling). flock locks are released by the kernel when the process dies,
so a crashed job can never leave a stale slot behind.
"""
from __future__ import annotations

import fcntl
import os
import sys
import time

LOCK_DIR = os.path.expanduser(os.environ.get("ENGRAVE_LOCK_DIR", "~/.cache/engrave/locks"))


class GpuSlot:
    def __init__(self, slots: int | None = None, poll: float = 2.0, label: str = ""):
        self.slots = int(slots or os.environ.get("ENGRAVE_GPU_SLOTS", 2))
        self.poll = poll
        self.label = label
        self.fh = None
        self.slot = None

    def acquire(self):
        os.makedirs(LOCK_DIR, exist_ok=True)
        t0 = time.time()
        said = False
        while True:
            for i in range(self.slots):
                fh = open(os.path.join(LOCK_DIR, f"gpu_slot_{i}.lock"), "a+")
                try:
                    fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    fh.close()
                    continue
                fh.seek(0)
                fh.truncate()
                fh.write(f"pid {os.getpid()} {self.label} since {time.strftime('%H:%M:%S')}\n")
                fh.flush()
                self.fh, self.slot = fh, i
                if said:
                    print(f"[gpulock] got slot {i} after {time.time() - t0:.0f}s", file=sys.stderr, flush=True)
                return self
            if not said:
                held = []
                for i in range(self.slots):
                    try:
                        with open(os.path.join(LOCK_DIR, f"gpu_slot_{i}.lock")) as f:
                            held.append(f.read().strip())
                    except OSError:
                        pass
                print(f"[gpulock] all {self.slots} GPU slots busy ({'; '.join(held)}); waiting...",
                      file=sys.stderr, flush=True)
                said = True
            time.sleep(self.poll)

    def release(self):
        if self.fh:
            fcntl.flock(self.fh, fcntl.LOCK_UN)
            self.fh.close()
            self.fh = None

    def __enter__(self):
        return self.acquire()

    def __exit__(self, *exc):
        self.release()
