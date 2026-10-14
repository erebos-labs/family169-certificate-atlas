#!/usr/bin/env python3
"""Exact bounded family-169 generator. No imported mathematical implementation.

The independent checker is verify.py, which deliberately does not import this file.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, permutations
import hashlib
import json
from pathlib import Path
import sys
import time

PIN = "1581d4cbdd69a0faf34b2089614fe2a814316a6a"
VERSION = "1.0.0"
LIMIT = 6


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def h_sequences(n: int):
    """Generate every weakly increasing extensive 1-based h once."""
    def visit(prefix):
        i = len(prefix) + 1
        if i > n:
            yield tuple(prefix)
            return
        for x in range(max(i, prefix[-1] if prefix else 1), n + 1):
            yield from visit(prefix + [x])
    yield from visit([])


def partitions(total: int, bound: int | None = None):
    if total == 0:
        yield ()
        return
    if bound is None:
        bound = total
    for first in range(min(total, bound), 0, -1):
        for rest in partitions(total - first, first):
            yield (first,) + rest


def compositions(total: int, length: int):
    if length == 0:
        if total == 0:
            yield ()
        return
    for first in range(total + 1):
        for rest in compositions(total - first, length - 1):
            yield (first,) + rest


def edges_of(h):
    return [(i, j) for i, hi in enumerate(h, 1) for j in range(i + 1, hi + 1)]


def colouring_polynomial(h):
    """Backtrack over all n available colours, pruning only improper prefixes.

    Keys are (the FULL length-n exponent vector, ascent degree), never orbits.
    Empty input has exactly one empty colouring and monomial.
    """
    n = len(h)
    earlier = [[i for i in range(j) if j + 1 <= h[i]] for j in range(n)]
    colors = [-1] * n
    powers = [0] * n
    result = Counter()
    visited = 0
    def visit(j, d):
        nonlocal visited
        visited += 1
        if j == n:
            result[tuple(powers), d] += 1
            return
        for c in range(n):
            if any(colors[i] == c for i in earlier[j]):
                continue
            colors[j] = c
            powers[c] += 1
            visit(j + 1, d + sum(colors[i] < c for i in earlier[j]))
            powers[c] -= 1
        colors[j] = -1
    visit(0, 0)
    return result, visited


def permitted(h):
    """Adjacent NONEDGE DESCENTS forbidden; graph inversions use all pairs."""
    n = len(h)
    edge_set = set(edges_of(h))
    def edge(a, b):
        return (min(a, b), max(a, b)) in edge_set
    result = defaultdict(list)
    for p in permutations(range(1, n + 1)):
        ok = all(a < b or edge(a, b) for a, b in zip(p, p[1:]))
        rev = p[::-1]
        admissible_rev = all(a > b or edge(a, b) for a, b in zip(rev, rev[1:]))
        require(ok == admissible_rev, "reversal/domain mismatch")
        degree = sum(p[i] > p[j] and edge(p[i], p[j])
                     for i in range(n) for j in range(i + 1, n))
        reverse_degree = sum(rev[i] > rev[j] and edge(rev[i], rev[j])
                             for i in range(n) for j in range(i + 1, n))
        require(degree + reverse_degree == len(edge_set), "reversal/degree mismatch")
        if ok:
            result[degree].append(p)
    return result


@lru_cache(maxsize=None)
def elementary_expansion(n: int, lam: tuple):
    """Multiply elementary subset sums by sparse polynomial convolution."""
    polynomial = Counter({(0,) * n: 1})
    for k in lam:
        nxt = Counter()
        for alpha, count in polynomial.items():
            for subset in combinations(range(n), k):
                beta = list(alpha)
                for c in subset:
                    beta[c] += 1
                nxt[tuple(beta)] += count
        polynomial = nxt
    return polynomial


def inverse_and_determinant(matrix):
    """Exact Gauss-Jordan, including row-swap determinant signs."""
    size = len(matrix)
    a = [[Fraction(x) for x in row] +
         [Fraction(int(i == j)) for j in range(size)]
         for i, row in enumerate(matrix)]
    determinant = Fraction(1)
    for col in range(size):
        pivot = next((i for i in range(col, size) if a[i][col]), None)
        require(pivot is not None, "singular elementary transition matrix")
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
            determinant *= -1
        scale = a[col][col]
        determinant *= scale
        a[col] = [x / scale for x in a[col]]
        for row in range(size):
            if row == col:
                continue
            scale = a[row][col]
            a[row] = [x - scale * y for x, y in zip(a[row], a[col])]
    require(all(a[i][j] == int(i == j) for i in range(size) for j in range(size)),
            "inverse reduction failed")
    inv = [row[size:] for row in a]
    require(all(sum(Fraction(matrix[i][k]) * inv[k][j] for k in range(size))
                == int(i == j) for i in range(size) for j in range(size)),
            "inverse multiplication failed")
    return inv, determinant


def make_basis(n):
    ps = sorted(partitions(n))
    representatives = [p + (0,) * (n - len(p)) for p in ps]
    matrix = [[elementary_expansion(n, lam).get(alpha, 0) for lam in ps]
              for alpha in representatives]
    inv, determinant = inverse_and_determinant(matrix)
    require(determinant.denominator == 1, "nonintegral determinant")
    require(abs(determinant) == 1, "transition matrix not unimodular")
    require(all(x.denominator == 1 for row in inv for x in row), "nonintegral inverse")
    data = {"n": n, "partitions": ps, "representatives": representatives,
            "matrix_rows_mu_columns_lambda": matrix,
            "inverse_rows_lambda_columns_mu": [[int(x) for x in row] for row in inv],
            "determinant": int(determinant)}
    return ps, representatives, inv, data


def certificate(h, basis):
    n = len(h)
    edges = edges_of(h)
    m = len(edges)
    raw, nodes = colouring_polynomial(h)
    ps, reps, inverse, _ = basis
    # Check symmetry on ALL weak compositions, including missing/zero monomials.
    symmetry_comparisons = 0
    for alpha in compositions(n, n):
        representative = tuple(sorted(alpha, reverse=True))
        for d in range(m + 1):
            require(raw.get((alpha, d), 0) == raw.get((representative, d), 0),
                    f"symmetry mismatch h={h} alpha={alpha} d={d}")
            symmetry_comparisons += 1
    coeff = [[0] * (m + 1) for _ in ps]
    for d in range(m + 1):
        b = [raw.get((alpha, d), 0) for alpha in reps]
        for j in range(len(ps)):
            x = sum(inverse[j][i] * b[i] for i in range(len(ps)))
            require(x.denominator == 1, f"nonintegral elementary coefficient h={h}")
            require(x >= 0, f"negative elementary coefficient h={h} d={d} lam={ps[j]}")
            coeff[j][d] = int(x)
    reconstructed = Counter()
    for lam, degrees in zip(ps, coeff):
        for d, count in enumerate(degrees):
            if count:
                for alpha, multiplicity in elementary_expansion(n, lam).items():
                    reconstructed[alpha, d] += count * multiplicity
    require(dict(reconstructed) == dict(raw), f"full basis reconstruction mismatch h={h}")
    perm = permitted(h)
    for d in range(m + 1):
        require(sum(c[d] for c in coeff) == len(perm[d]),
                f"coefficient-count identity mismatch h={h} d={d}")
    rows = []
    for d in range(m + 1):
        pool = perm[d]  # itertools.permutations of sorted labels is lexicographic.
        slots = [lam for lam, counts in zip(ps, coeff) for _ in range(counts[d])]
        require(len(pool) == len(slots), "slot count mismatch")
        rows.extend({"permutation": p, "degree": d, "partition": lam}
                    for p, lam in zip(pool, slots))
    rows.sort(key=lambda row: tuple(row["permutation"]))
    terms = [{"partition": lam, "q_coefficients": counts}
             for lam, counts in zip(ps, coeff) if any(counts)]
    output = {"schema": "family169-certificate-v1", "source_commit": PIN,
              "n": n, "h": h, "edges": edges,
              "monomials": [{"alpha": a, "degree": d, "coefficient": c}
                            for (a, d), c in sorted(raw.items())],
              "elementary": terms, "witness": rows}
    stats = {"n": n, "h": h, "edges": m, "proper_colourings": sum(raw.values()),
             "monomial_q_entries": len(raw), "permitted_permutations": len(rows),
             "colouring_prefix_nodes": nodes, "symmetry_comparisons": symmetry_comparisons,
             "nonzero_elementary_q_entries": sum(x != 0 for c in coeff for x in c)}
    return output, stats


def write_json(path: Path, obj):
    data = (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if path.exists():
        require(path.read_bytes() == data, f"refusing to overwrite changed baseline: {path}")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def cert_relative(n, h):
    suffix = "_".join(map(str, h)) if h else "empty"
    return f"certificates/n{n:02d}/h_{suffix}.json"


def build_catalog(root: Path, max_n: int):
    records = []
    for n in range(max_n + 1):
        for h in h_sequences(n):
            relative = cert_relative(n, h)
            path = root / relative
            require(path.exists(), f"missing predecessor certificate {path}")
            records.append({"n": n, "h": h, "path": relative,
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    obj = {"schema": "family169-atlas-v1", "version": VERSION, "source_commit": PIN,
           "min_n": 0, "max_n": max_n, "graphs": records}
    # The catalog is the only intentionally extended data file; snapshot each stage.
    data = json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n"
    (root / "atlas.json").write_text(data)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--min-n", type=int, default=0)
    ap.add_argument("--max-n", type=int, default=4)
    args = ap.parse_args()
    require(0 <= args.min_n <= args.max_n <= LIMIT, "hard scope limit: 0 <= n <= 6")
    args.out.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    for n in range(args.min_n, args.max_n + 1):
        ns = time.perf_counter()
        basis = make_basis(n)
        write_json(args.out / "basis" / f"n{n:02d}.json", basis[3])
        graph_count = 0
        for h in h_sequences(n):
            gs = time.perf_counter()
            try:
                obj, stats = certificate(h, basis)
            except Exception:
                # Stop immediately; no later graph or size is generated.
                (args.out / "FAILED_INPUT.json").write_text(json.dumps({"n": n, "h": h}))
                raise
            digest = write_json(args.out / cert_relative(n, h), obj)
            stats.update(event="generated", seconds=time.perf_counter() - gs, sha256=digest)
            print(json.dumps(stats, sort_keys=True), flush=True)
            graph_count += 1
        print(json.dumps({"event": "size_generated", "n": n, "graphs": graph_count,
                          "seconds": time.perf_counter() - ns}), flush=True)
    build_catalog(args.out, args.max_n)
    print(json.dumps({"event": "generation_pass", "min_n": args.min_n,
                      "max_n": args.max_n, "seconds": time.perf_counter() - started}), flush=True)


if __name__ == "__main__":
    main()
