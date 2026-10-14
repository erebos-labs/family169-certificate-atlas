#!/usr/bin/env python3
"""Standalone exhaustive certificate checker, using only the Python standard library.

No generator import, basis conversion, general positivity theorem, graph-isomorphism
reduction, or precomputed colouring/permutation answers are used in acceptance.
SPDX-License-Identifier: Apache-2.0
"""
from __future__ import annotations
import argparse
from collections import Counter
from functools import lru_cache
from itertools import combinations_with_replacement, product
import hashlib
import json
from math import factorial
from pathlib import Path
import time

PIN = "1581d4cbdd69a0faf34b2089614fe2a814316a6a"
LIMIT = 6


class VerificationError(ValueError):
    def __init__(self, code, detail=""):
        self.code = code
        super().__init__(f"{code}: {detail}")


def check(condition, code, detail=""):
    if not condition:
        raise VerificationError(code, detail)


def integer(value, low, high, code):
    check(type(value) is int and low <= value <= high, code, repr(value))


def strict_pairs(pairs):
    result = {}
    for key, value in pairs:
        check(key not in result, "duplicate_json_key", key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(Path(path).read_text(), object_pairs_hook=strict_pairs)


def all_h(n):
    # A different construction from the generator: combinations with replacement.
    for h in combinations_with_replacement(range(1, n + 1), n):
        if all(value >= i + 1 for i, value in enumerate(h)):
            yield h


def all_partitions(n):
    out = []
    for length in range(n + 1):
        for parts in combinations_with_replacement(range(1, n + 1), length):
            if sum(parts) == n:
                out.append(parts[::-1])
    return sorted(out)


def permutation_words(n):
    """Lexicographic successor enumeration, independent of itertools.permutations."""
    word = list(range(1, n + 1))
    while True:
        yield tuple(word)
        i = n - 2
        while i >= 0 and word[i] >= word[i + 1]:
            i -= 1
        if i < 0:
            return
        j = n - 1
        while word[j] <= word[i]:
            j -= 1
        word[i], word[j] = word[j], word[i]
        word[i + 1:] = reversed(word[i + 1:])


def adjacency(h):
    n = len(h)
    a = [[False] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if j + 1 <= h[i]:
                a[i][j] = a[j][i] = True
    edges = [(i + 1, j + 1) for i in range(n) for j in range(i + 1, n) if a[i][j]]
    return a, edges


def domain_and_degrees(n, adj, edges):
    result = {}
    visited = 0
    for word in permutation_words(n):
        visited += 1
        allowed = not any(word[i] > word[i + 1] and
                          not adj[word[i] - 1][word[i + 1] - 1]
                          for i in range(n - 1))
        reversed_word = word[::-1]
        allowed_reversed = not any(reversed_word[i] < reversed_word[i + 1] and
                                   not adj[reversed_word[i] - 1][reversed_word[i + 1] - 1]
                                   for i in range(n - 1))
        check(allowed == allowed_reversed, "internal_reversal_domain")
        position = {letter: i for i, letter in enumerate(word)}
        # An edge a<b is inverted iff b appears before a. No position-pair loop.
        degree = sum(position[b] < position[a] for a, b in edges)
        reverse_position = {letter: i for i, letter in enumerate(reversed_word)}
        check(degree + sum(reverse_position[b] < reverse_position[a] for a, b in edges)
              == len(edges), "internal_reversal_degree")
        if allowed:
            result[word] = degree
    check(visited == factorial(n), "internal_permutation_coverage")
    return result, visited


def enumerate_colours(n, adj):
    """Visit ALL n**n functions (0**0=1), then filter for properness."""
    result = Counter()
    visited = 0
    for colours in product(range(n), repeat=n):
        visited += 1
        if any(adj[i][j] and colours[i] == colours[j]
               for i in range(n) for j in range(i + 1, n)):
            continue
        degree = sum(adj[i][j] and colours[i] < colours[j]
                     for i in range(n) for j in range(i + 1, n))
        alpha = tuple(colours.count(c) for c in range(n))
        result[alpha, degree] += 1
    check(visited == n ** n, "internal_colour_coverage")
    return result, visited


@lru_cache(maxsize=None)
def expand_elementary(n, partition):
    """Direct 0/1 incidence-matrix enumeration, NOT a basis change or convolution.

    Each factor is a labelled row. Its mask is a subset of the n colours having
    the prescribed row sum. Column sums are the monomial exponent vector.
    Repeated equal factors still occupy different rows and retain multiplicity.
    """
    choices = [tuple(mask for mask in range(1 << n) if mask.bit_count() == k)
               for k in partition]
    result = Counter()
    for matrix in product(*choices):
        alpha = tuple(sum((row >> c) & 1 for row in matrix) for c in range(n))
        result[alpha] += 1
    return result


def parse_partition(parts, n):
    check(type(parts) is list, "partition_type")
    for part in parts:
        integer(part, 1, n, "partition_part")
    check(parts == sorted(parts, reverse=True) and sum(parts) == n, "partition_validity")
    return tuple(parts)


def first_difference(a, b):
    for key in sorted(set(a) | set(b)):
        if a.get(key, 0) != b.get(key, 0):
            return repr({"key": key, "left": a.get(key, 0), "right": b.get(key, 0)})
    return ""


def verify_graph(obj):
    started = time.perf_counter()
    check(type(obj) is dict and set(obj) == {
        "schema", "source_commit", "n", "h", "edges", "monomials", "elementary", "witness"
    }, "certificate_fields")
    check(obj["schema"] == "family169-certificate-v1" and obj["source_commit"] == PIN,
          "certificate_identity")
    n = obj["n"]
    integer(n, 0, LIMIT, "size_bound")
    h = obj["h"]
    check(type(h) is list and len(h) == n, "h_length")
    for i, value in enumerate(h):
        integer(value, i + 1, n, "h_extensive")
    check(h == sorted(h), "h_monotone")
    adj, edges = adjacency(h)
    check(obj["edges"] == [list(e) for e in edges], "edge_list")
    m = len(edges)
    permitted, all_permutations = domain_and_degrees(n, adj, edges)
    witness = obj["witness"]
    check(type(witness) is list, "witness_type")
    seen = set()
    bins = Counter()
    for row in witness:
        check(type(row) is dict and set(row) == {"permutation", "degree", "partition"},
              "witness_row_fields")
        p = row["permutation"]
        check(type(p) is list and len(p) == n, "permutation_length")
        for letter in p:
            integer(letter, 1, n, "permutation_letter")
        p = tuple(p)
        check(p not in seen, "duplicate_permutation", p)
        check(p in permitted, "nonpermitted_permutation", p)
        seen.add(p)
        d = row["degree"]
        integer(d, 0, m, "degree_bound")
        check(d == permitted[p], "wrong_graph_inversion_degree", p)
        lam = parse_partition(row["partition"], n)
        bins[lam, d] += 1
    check(seen == set(permitted), "missing_permutation", sorted(set(permitted) - seen)[:1])
    # Read the supplied elementary coefficients only as a redundant summary of rows.
    summary = Counter()
    summary_shapes = set()
    check(type(obj["elementary"]) is list, "elementary_type")
    for row in obj["elementary"]:
        check(type(row) is dict and set(row) == {"partition", "q_coefficients"},
              "elementary_row_fields")
        lam = parse_partition(row["partition"], n)
        check(lam not in summary_shapes, "duplicate_elementary_shape")
        summary_shapes.add(lam)
        coeff = row["q_coefficients"]
        check(type(coeff) is list and len(coeff) == m + 1, "elementary_degree_length")
        for d, count in enumerate(coeff):
            integer(count, 0, len(permitted), "elementary_integer_nonnegative")
            if count:
                summary[lam, d] = count
        check(any(coeff), "redundant_zero_elementary_shape")
    check(dict(summary) == dict(bins), "elementary_summary", first_difference(summary, bins))
    degree_counts = Counter(permitted.values())
    for d in range(m + 1):
        check(sum(count for (lam, degree), count in summary.items() if degree == d)
              == degree_counts[d], "coefficient_count_identity", d)
    recorded_raw = {}
    check(type(obj["monomials"]) is list, "monomial_type")
    for row in obj["monomials"]:
        check(type(row) is dict and set(row) == {"alpha", "degree", "coefficient"},
              "monomial_row_fields")
        alpha = row["alpha"]
        check(type(alpha) is list and len(alpha) == n, "alpha_length")
        for exponent in alpha:
            integer(exponent, 0, n, "alpha_exponent")
        check(sum(alpha) == n, "alpha_total_degree")
        d, count = row["degree"], row["coefficient"]
        integer(d, 0, m, "monomial_degree_bound")
        integer(count, 1, n ** n, "monomial_coefficient")
        key = tuple(alpha), d
        check(key not in recorded_raw, "duplicate_monomial_entry")
        recorded_raw[key] = count
    actual_raw, candidates = enumerate_colours(n, adj)
    check(recorded_raw == dict(actual_raw), "colouring_table_mismatch",
          first_difference(recorded_raw, actual_raw))
    # Adjacent coordinate transpositions generate the full symmetric group.
    # Checking each nonzero entry also detects a swap to a missing (zero) entry.
    symmetry_checks = 0
    for (alpha, d), count in actual_raw.items():
        for i in range(n - 1):
            beta = list(alpha)
            beta[i], beta[i + 1] = beta[i + 1], beta[i]
            check(actual_raw.get((tuple(beta), d), 0) == count, "symmetry_failure")
            symmetry_checks += 1
        # A separate reversal check guards the colour ascent/inversion convention.
        check(actual_raw.get((alpha[::-1], m - d), 0) == count, "colour_reversal_failure")
    rhs = Counter()
    for (lam, d), count in bins.items():
        for alpha, multiplicity in expand_elementary(n, lam).items():
            rhs[alpha, d] += count * multiplicity
    check(dict(rhs) == dict(actual_raw), "coefficient_identity",
          first_difference(actual_raw, rhs))
    return {"event": "verified", "n": n, "h": h, "edges": m,
            "colour_candidates": candidates, "proper_colourings": sum(actual_raw.values()),
            "all_permutations": all_permutations, "permitted_permutations": len(permitted),
            "monomial_q_entries": len(actual_raw), "symmetry_comparisons": symmetry_checks,
            "nonzero_elementary_q_entries": len(bins), "seconds": time.perf_counter() - started}


def determinant_bareiss(matrix):
    a = [row[:] for row in matrix]
    size = len(a)
    previous = 1
    sign = 1
    for k in range(size - 1):
        pivot_row = next((i for i in range(k, size) if a[i][k]), None)
        check(pivot_row is not None, "basis_singular")
        if pivot_row != k:
            a[k], a[pivot_row] = a[pivot_row], a[k]
            sign *= -1
        pivot = a[k][k]
        for i in range(k + 1, size):
            for j in range(k + 1, size):
                numerator = pivot * a[i][j] - a[i][k] * a[k][j]
                check(numerator % previous == 0, "internal_bareiss_division")
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = pivot
    return sign * a[-1][-1]


def audit_basis(path, n):
    """Supplementary independent audit. This data is NOT used by verify_graph."""
    obj = read_json(path)
    ps = all_partitions(n)
    check(obj["n"] == n and obj["partitions"] == [list(p) for p in ps], "basis_partitions")
    reps = [p + (0,) * (n - len(p)) for p in ps]
    check(obj["representatives"] == [list(a) for a in reps], "basis_representatives")
    expected = [[expand_elementary(n, p).get(a, 0) for p in ps] for a in reps]
    matrix = obj["matrix_rows_mu_columns_lambda"]
    check(matrix == expected, "basis_matrix")
    inv = obj["inverse_rows_lambda_columns_mu"]
    size = len(ps)
    check(type(inv) is list and len(inv) == size, "basis_inverse_size")
    check(all(type(row) is list and len(row) == size and all(type(x) is int for x in row)
              for row in inv), "basis_inverse_integer")
    check(all(sum(matrix[i][k] * inv[k][j] for k in range(size)) == int(i == j)
              for i in range(size) for j in range(size)), "basis_inverse_product")
    det = determinant_bareiss(matrix)
    check(type(obj["determinant"]) is int and obj["determinant"] == det and abs(det) == 1,
          "basis_determinant")
    return {"event": "basis_verified", "n": n, "dimension": size, "determinant": det}


def expected_relative(n, h):
    suffix = "_".join(str(x) for x in h) if h else "empty"
    return f"certificates/n{n:02d}/h_{suffix}.json"


def validate_catalog(root):
    root = Path(root)
    catalog = read_json(root / "atlas.json")
    check(type(catalog) is dict and set(catalog) == {
        "schema", "version", "source_commit", "min_n", "max_n", "graphs"
    }, "catalog_fields")
    check(catalog["schema"] == "family169-atlas-v1" and catalog["version"] == "1.0.0"
          and catalog["source_commit"] == PIN and catalog["min_n"] == 0, "catalog_identity")
    integer(catalog["max_n"], 0, LIMIT, "catalog_scope")
    expected = [(n, h) for n in range(catalog["max_n"] + 1) for h in all_h(n)]
    records = catalog["graphs"]
    check(type(records) is list and len(records) == len(expected), "catalog_graph_count")
    paths = set()
    for row, (n, h) in zip(records, expected):
        check(type(row) is dict and set(row) == {"n", "h", "path", "sha256"}, "catalog_row_fields")
        check(type(row["n"]) is int and row["n"] == n and row["h"] == list(h), "catalog_graph_order")
        relative = expected_relative(n, h)
        check(row["path"] == relative and relative not in paths, "catalog_path")
        paths.add(relative)
        file_path = root / relative
        check(file_path.is_file(), "missing_certificate", relative)
        check(hashlib.sha256(file_path.read_bytes()).hexdigest() == row["sha256"],
              "certificate_hash", relative)
    actual_paths = {p.relative_to(root).as_posix() for p in (root / "certificates").rglob("*.json")}
    check(paths == actual_paths, "uncatalogued_certificate")
    return catalog


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--atlas", type=Path, required=True)
    ap.add_argument("--min-n", type=int, default=0)
    ap.add_argument("--max-n", type=int)
    ap.add_argument("--skip-basis", action="store_true", help="the core identity check never uses basis data")
    args = ap.parse_args()
    started = time.perf_counter()
    catalog = validate_catalog(args.atlas)
    max_n = catalog["max_n"] if args.max_n is None else args.max_n
    check(0 <= args.min_n <= max_n <= catalog["max_n"], "verification_scope")
    by_n = Counter()
    seconds = Counter()
    for row in catalog["graphs"]:
        if args.min_n <= row["n"] <= max_n:
            obj = read_json(args.atlas / row["path"])
            check(obj["n"] == row["n"] and obj["h"] == row["h"], "certificate_graph_binding")
            stats = verify_graph(obj)
            print(json.dumps(stats, sort_keys=True), flush=True)
            by_n[row["n"]] += 1
            seconds[row["n"]] += stats["seconds"]
    for n in range(args.min_n, max_n + 1):
        check(by_n[n] == sum(1 for _ in all_h(n)), "verified_size_coverage")
        if not args.skip_basis:
            print(json.dumps(audit_basis(args.atlas / "basis" / f"n{n:02d}.json", n)), flush=True)
        print(json.dumps({"event": "size_verified", "n": n, "graphs": by_n[n],
                          "graph_check_seconds": seconds[n]}), flush=True)
    print(json.dumps({"event": "verification_pass", "min_n": args.min_n, "max_n": max_n,
                      "graphs": sum(by_n.values()), "seconds": time.perf_counter() - started}), flush=True)


if __name__ == "__main__":
    main()
