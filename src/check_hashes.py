#!/usr/bin/env python3
"""Check packaged files against SHA256SUMS. SPDX-License-Identifier: Apache-2.0"""
from pathlib import Path
import hashlib
import re


def main():
    root = Path(__file__).resolve().parents[1]
    seen = set()
    for line in (root / "SHA256SUMS").read_text().splitlines():
        digest, relative = line.split("  ", 1)
        if re.fullmatch(r"[0-9a-f]{64}", digest) is None or relative in seen:
            raise ValueError("invalid or repeated checksum entry")
        seen.add(relative)
        path = root / relative
        if not path.resolve().is_relative_to(root) or not path.is_file():
            raise ValueError("missing or escaping file: " + relative)
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("checksum mismatch: " + relative)
    print(f"PASS: {len(seen)} packaged file hashes match SHA256SUMS")


if __name__ == "__main__":
    main()
