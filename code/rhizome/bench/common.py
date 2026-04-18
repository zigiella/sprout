"""Common helpers for the Rhizome benchmark harness."""

from __future__ import annotations

import ctypes
import math
import platform
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parents[1]
BENCH_DIR = ROOT_DIR / "bench"
BENCHMARKS_DIR = ROOT_DIR / "benchmarks"
DEFAULT_PROMPT_SET_PATH = BENCH_DIR / "prompt_set.jsonl"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(value: str) -> str:
    collapsed = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return collapsed.strip("-") or "unknown"


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    rank = (len(ordered) - 1) * pct
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[lower]
    weight = rank - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def bytes_to_gib(value: int | None) -> float | None:
    if value is None:
        return None
    return round(value / (1024**3), 3)


def _read_windows_memory_snapshot() -> tuple[int, int] | None:
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [
            ("dwLength", ctypes.c_ulong),
            ("dwMemoryLoad", ctypes.c_ulong),
            ("ullTotalPhys", ctypes.c_ulonglong),
            ("ullAvailPhys", ctypes.c_ulonglong),
            ("ullTotalPageFile", ctypes.c_ulonglong),
            ("ullAvailPageFile", ctypes.c_ulonglong),
            ("ullTotalVirtual", ctypes.c_ulonglong),
            ("ullAvailVirtual", ctypes.c_ulonglong),
            ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
        ]

    stat = MEMORYSTATUSEX()
    stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    kernel32 = ctypes.windll.kernel32
    if kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)) == 0:
        return None
    return int(stat.ullTotalPhys), int(stat.ullAvailPhys)


def _read_linux_memory_snapshot() -> tuple[int, int] | None:
    meminfo_path = Path("/proc/meminfo")
    if not meminfo_path.exists():
        return None

    raw: dict[str, int] = {}
    for line in meminfo_path.read_text(encoding="utf-8").splitlines():
        name, value = line.split(":", maxsplit=1)
        raw[name] = int(value.strip().split()[0]) * 1024
    total = raw.get("MemTotal")
    available = raw.get("MemAvailable")
    if total is None or available is None:
        return None
    return total, available


def read_memory_snapshot() -> dict[str, int] | None:
    snapshot: tuple[int, int] | None
    if sys.platform == "win32":
        snapshot = _read_windows_memory_snapshot()
    else:
        snapshot = _read_linux_memory_snapshot()
    if snapshot is None:
        return None
    total, available = snapshot
    return {"total_bytes": total, "available_bytes": available, "used_bytes": total - available}


def get_total_memory_bytes() -> int | None:
    snapshot = read_memory_snapshot()
    if snapshot is None:
        return None
    return snapshot["total_bytes"]


def detect_host() -> dict[str, Any]:
    host: dict[str, Any] = {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor() or None,
        "python_version": platform.python_version(),
        "total_memory_bytes": get_total_memory_bytes(),
    }

    if sys.platform == "win32":
        try:
            command = [
                "powershell",
                "-Command",
                "$cs=Get-CimInstance Win32_ComputerSystem; "
                "[Console]::WriteLine(($cs.Manufacturer + '|' + $cs.Model))",
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=10)
            manufacturer, model = result.stdout.strip().split("|", maxsplit=1)
            host["manufacturer"] = manufacturer.strip()
            host["model"] = model.strip()
        except Exception:
            host["manufacturer"] = None
            host["model"] = None
    else:
        vendor_path = Path("/sys/class/dmi/id/sys_vendor")
        model_path = Path("/sys/class/dmi/id/product_name")
        host["manufacturer"] = vendor_path.read_text(encoding="utf-8").strip() if vendor_path.exists() else None
        host["model"] = model_path.read_text(encoding="utf-8").strip() if model_path.exists() else None

    return host


@dataclass
class MemorySampler:
    """Best-effort system memory sampler."""

    interval_s: float = 0.1

    def __post_init__(self) -> None:
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._peak_used_bytes: int | None = None
        self._samples = 0

    def _run(self) -> None:
        while not self._stop_event.is_set():
            snapshot = read_memory_snapshot()
            if snapshot is not None:
                used_bytes = snapshot["used_bytes"]
                self._peak_used_bytes = used_bytes if self._peak_used_bytes is None else max(self._peak_used_bytes, used_bytes)
                self._samples += 1
            time.sleep(self.interval_s)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        self._thread.join(timeout=max(1.0, self.interval_s * 4))

    @property
    def peak_used_bytes(self) -> int | None:
        return self._peak_used_bytes

    @property
    def samples(self) -> int:
        return self._samples
