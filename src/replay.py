#!/usr/bin/env python3
"""Rebuild in a NEW directory, with the original staged budget gate, then verify.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", type=Path, required=True, help="must not exist")
    ap.add_argument("--reference", type=Path, default=Path(__file__).resolve().parents[1] / "atlas")
    ap.add_argument("--budget-seconds", type=float, default=7200)
    a = ap.parse_args()
    if a.output.exists() or not 0 < a.budget_seconds <= 7200:
        ap.error("output must be new; budget must be in (0,7200]")
    a.output = a.output.resolve()
    a.reference = a.reference.resolve()
    a.output.mkdir(parents=True)
    source = Path(__file__).resolve().parent
    data = a.output / "atlas"
    logs = a.output / "logs"
    logs.mkdir()
    started = time.perf_counter()
    metrics = []
    def stage(name, script, *arguments):
        remaining = a.budget_seconds - (time.perf_counter() - started)
        if remaining <= 0:
            raise RuntimeError("aggregate compute wall-time budget exhausted")
        command = [sys.executable, str(source / "run_stage.py"), "--log", str(logs / (name + ".log")),
                   "--timeout", str(remaining), "--", sys.executable, "-u", str(source / script),
                   *map(str, arguments)]
        subprocess.run(command, check=True)
        measured = json.loads((logs / (name + ".metrics.json")).read_text())
        metrics.append(measured)
        return measured
    def freeze(tag):
        shutil.copyfile(data / "atlas.json", a.output / (tag + "_atlas.json"))
        return {p.relative_to(data).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in data.rglob("*.json") if p.name != "atlas.json"}
    def preserve(snapshot):
        for relative, digest in snapshot.items():
            if hashlib.sha256((data / relative).read_bytes()).hexdigest() != digest:
                raise RuntimeError("baseline changed: " + relative)
    stage("generate_0_4", "generate.py", "--out", data, "--max-n", 4)
    stage("verify_0_4", "verify.py", "--atlas", data)
    stage("tests_0_4", "mutation_tests.py", "--atlas", data)
    small = freeze("n_le4")
    g5 = stage("generate_5", "generate.py", "--out", data, "--min-n", 5, "--max-n", 5)
    v5 = stage("verify_5", "verify.py", "--atlas", data, "--min-n", 5, "--max-n", 5)
    preserve(small)
    middle = freeze("n_le5")
    projected_time = 3 * ((132 * 6**6) / (42 * 5**5)) * (g5["elapsed_seconds"] + v5["elapsed_seconds"]) + 60
    projected_memory = 8 * max(g5["peak_child_rss_bytes"], v5["peak_child_rss_bytes"])
    permitted = (time.perf_counter() - started) + projected_time < a.budget_seconds and projected_memory < 2_000_000_000
    gate = {"decision": "proceed" if permitted else "stop", "projected_n6_seconds": projected_time,
            "projected_rss_bytes": projected_memory, "budget_seconds": a.budget_seconds,
            "memory_cap_bytes": 2_000_000_000,
            "note": "Conservative projection from measured n=5 stages, not a complexity proof."}
    (logs / "budget_gate.json").write_text(json.dumps(gate, indent=2) + "\n")
    if not permitted:
        print(json.dumps({"event": "replay_bounded_stop", "largest_verified_n": 5, **gate}))
        return
    stage("generate_6", "generate.py", "--out", data, "--min-n", 6, "--max-n", 6)
    stage("verify_0_6", "verify.py", "--atlas", data)
    stage("tests_0_6", "mutation_tests.py", "--atlas", data)
    preserve(small)
    preserve(middle)
    reference_files = sorted(p.relative_to(a.reference) for p in a.reference.rglob("*.json"))
    replay_files = sorted(p.relative_to(data) for p in data.rglob("*.json"))
    if reference_files != replay_files:
        raise RuntimeError("replay/reference file sets differ")
    for relative in reference_files:
        if (a.reference / relative).read_bytes() != (data / relative).read_bytes():
            raise RuntimeError("replay differs: " + relative.as_posix())
    result = {"event": "replay_pass", "max_n": 6, "graphs": 197,
              "byte_identical_dataset_files": len(reference_files),
              "elapsed_seconds": time.perf_counter() - started,
              "stage_wall_seconds": sum(m["elapsed_seconds"] for m in metrics),
              "peak_child_rss_bytes": max(m["peak_child_rss_bytes"] for m in metrics)}
    (a.output / "replay_summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
