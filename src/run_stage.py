#!/usr/bin/env python3
"""Run one synchronous, resource-bounded stage and preserve its actual output.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import datetime
import json
from pathlib import Path
import platform
import resource
import subprocess
import sys
import time


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--log", type=Path, required=True)
    ap.add_argument("--timeout", type=float, default=7200)
    ap.add_argument("command", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    command = a.command[1:] if a.command[:1] == ["--"] else a.command
    if not command:
        ap.error("command required")
    a.log.parent.mkdir(parents=True, exist_ok=True)
    if a.log.exists() or a.log.with_suffix(".metrics.json").exists():
        ap.error("refusing to overwrite existing logs")
    memory_limit = 2_000_000_000
    limit_applied = sys.platform.startswith("linux")
    def limits():
        if limit_applied:
            resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
    start = time.perf_counter()
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    timed_out = False
    with a.log.open("w") as output:
        try:
            result = subprocess.run(command, stdout=output, stderr=subprocess.STDOUT,
                                    timeout=a.timeout, preexec_fn=limits)
            code = result.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            code = 124
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    peak = usage.ru_maxrss if sys.platform == "darwin" else usage.ru_maxrss * 1024
    metrics = {"command": command, "started_utc": timestamp, "elapsed_seconds": time.perf_counter() - start,
               "child_user_seconds": usage.ru_utime, "child_system_seconds": usage.ru_stime,
               "peak_child_rss_bytes": peak, "address_space_limit_bytes": memory_limit if limit_applied else None,
               "timeout_seconds": a.timeout, "timed_out": timed_out, "return_code": code,
               "python": sys.version, "platform": platform.platform()}
    a.log.with_suffix(".metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps(metrics, sort_keys=True))
    lines = a.log.read_text().splitlines()
    print("Last log line:", lines[-1] if lines else "(empty)")
    sys.exit(code)


if __name__ == "__main__":
    main()
