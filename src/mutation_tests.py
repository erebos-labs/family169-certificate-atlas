#!/usr/bin/env python3
"""Positive regressions and semantic negative tests. SPDX-License-Identifier: Apache-2.0"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import time
import verify as V


def emit(event, **kw):
    print(json.dumps({"event": event, **kw}, sort_keys=True), flush=True)


def expect_failure(name, operation, expected_codes, **context):
    try:
        operation()
    except V.VerificationError as exc:
        V.check(exc.code in expected_codes, "wrong_mutation_failure", f"{name}: {exc}")
        emit("mutation_rejected", test=name, code=exc.code, **context)
        return 1
    raise V.VerificationError("mutation_accepted", name)


def refresh_summary(obj):
    m = len(obj["edges"])
    bins = Counter((tuple(row["partition"]), row["degree"]) for row in obj["witness"])
    obj["elementary"] = [
        {"partition": list(lam), "q_coefficients": [bins[lam, d] for d in range(m + 1)]}
        for lam in sorted({lam for lam, d in bins})
    ]


def regression(root):
    def load(n, h):
        return V.read_json(root / V.expected_relative(n, h))
    zero = load(0, ())
    V.verify_graph(zero)
    V.check(zero["monomials"] == [{"alpha": [], "degree": 0, "coefficient": 1}], "empty_colouring")
    V.check(zero["witness"] == [{"permutation": [], "degree": 0, "partition": []}], "empty_witness")
    one = load(1, (1,))
    V.verify_graph(one)
    V.check(one["elementary"] == [{"partition": [1], "q_coefficients": [1]}], "singleton_e")
    empty2 = load(2, (1, 2))
    V.verify_graph(empty2)
    V.check(sum(row["coefficient"] for row in empty2["monomials"]) == 4,
            "available_not_surjective_colours")
    V.check(empty2["elementary"] == [{"partition": [1, 1], "q_coefficients": [1]}], "empty2_e")
    complete2 = load(2, (2, 2))
    V.verify_graph(complete2)
    V.check(complete2["elementary"] == [{"partition": [2], "q_coefficients": [1, 1]}], "complete2_e")
    path = load(3, (2, 3, 3))
    V.verify_graph(path)
    V.check(path["elementary"] == [
        {"partition": [2, 1], "q_coefficients": [0, 1, 0]},
        {"partition": [3], "q_coefficients": [1, 1, 1]}], "paper_path_e")
    actual = {(tuple(x["alpha"]), x["degree"]): x["coefficient"] for x in path["monomials"]}
    expected = {((1, 1, 1), d): c for d, c in enumerate((1, 4, 1))}
    for alpha in [(2, 1, 0), (2, 0, 1), (1, 2, 0), (0, 2, 1), (1, 0, 2), (0, 1, 2)]:
        expected[alpha, 1] = 1
    V.check(actual == expected, "paper_path_monomials")
    by_word = {tuple(row["permutation"]): (row["degree"], tuple(row["partition"]))
               for row in path["witness"]}
    V.check(by_word == {(1, 2, 3): (0, (3,)), (1, 3, 2): (1, (2, 1)),
                        (2, 1, 3): (1, (3,)), (3, 2, 1): (2, (3,))}, "path_synthetic_allocation")
    # A simultaneous exchange within the same degree is a VALID different witness.
    # The checker verifies the identity, not uniqueness or the generator's order rule.
    alternative = deepcopy(path)
    for row in alternative["witness"]:
        if row["permutation"] == [1, 3, 2]:
            row["partition"] = [3]
        elif row["permutation"] == [2, 1, 3]:
            row["partition"] = [2, 1]
    V.verify_graph(alternative)
    emit("regressions_pass", tests=6, includes="n=0,n=1,empty2,complete2,path3,valid_alternative_path_witness")
    return path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--atlas", type=Path, required=True)
    ap.add_argument("--max-n", type=int)
    args = ap.parse_args()
    start = time.perf_counter()
    catalog = V.validate_catalog(args.atlas)
    cap = catalog["max_n"] if args.max_n is None else args.max_n
    V.check(3 <= cap <= catalog["max_n"], "test_range")
    path = regression(args.atlas)
    rejected = 0
    skipped = 0
    graphs = 0
    for entry in catalog["graphs"]:
        if entry["n"] > cap:
            continue
        obj = V.read_json(args.atlas / entry["path"])
        ctx = {"n": obj["n"], "h": obj["h"]}
        graphs += 1
        removed = deepcopy(obj)
        removed["witness"].pop(0)
        rejected += expect_failure("removed_permutation", lambda: V.verify_graph(removed),
                                   {"missing_permutation"}, **ctx)
        duplicated = deepcopy(obj)
        duplicated["witness"].append(deepcopy(duplicated["witness"][0]))
        rejected += expect_failure("duplicated_permutation", lambda: V.verify_graph(duplicated),
                                   {"duplicate_permutation"}, **ctx)
        degree = deepcopy(obj)
        m = len(degree["edges"])
        degree["witness"][0]["degree"] = (degree["witness"][0]["degree"] + 1) % (m + 1) if m else 1
        rejected += expect_failure("changed_degree", lambda: V.verify_graph(degree),
                                   {"degree_bound"} if m == 0 else {"wrong_graph_inversion_degree"}, **ctx)
        if obj["n"] >= 2:
            changed = deepcopy(obj)
            original = changed["witness"][0]["partition"]
            changed["witness"][0]["partition"] = [obj["n"]] if original != [obj["n"]] else [1] * obj["n"]
            refresh_summary(changed)  # Do NOT let a stale summary be the reason for rejection.
            rejected += expect_failure("changed_partition_with_consistent_summary",
                                       lambda: V.verify_graph(changed), {"coefficient_identity"}, **ctx)
        else:
            skipped += 1
            emit("mutation_inapplicable", test="different_valid_partition", reason="unique partition of n", **ctx)
    for name in ("changed_monomial", "removed_monomial", "duplicated_monomial"):
        obj = deepcopy(path)
        if name == "changed_monomial":
            obj["monomials"][0]["coefficient"] += 1
            code = "colouring_table_mismatch"
        elif name == "removed_monomial":
            obj["monomials"].pop()
            code = "colouring_table_mismatch"
        else:
            obj["monomials"].append(deepcopy(obj["monomials"][0]))
            code = "duplicate_monomial_entry"
        rejected += expect_failure(name, lambda: V.verify_graph(obj), {code}, n=3, h=[2, 3, 3])
    rejected += expect_failure("duplicate_json_key", lambda: json.loads('{"n":0,"n":1}', object_pairs_hook=V.strict_pairs),
                               {"duplicate_json_key"})
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        bad = deepcopy(catalog)
        bad["graphs"].pop()
        (root / "atlas.json").write_text(json.dumps(bad))
        rejected += expect_failure("removed_catalog_graph", lambda: V.validate_catalog(root), {"catalog_graph_count"})
        bad = deepcopy(catalog)
        bad["graphs"][0] = deepcopy(bad["graphs"][1])
        (root / "atlas.json").write_text(json.dumps(bad))
        rejected += expect_failure("duplicated_catalog_graph", lambda: V.validate_catalog(root), {"catalog_graph_order"})
    emit("mutation_suite_pass", graphs=graphs, rejected=rejected, inapplicable=skipped,
         max_n=cap, seconds=time.perf_counter() - start)


if __name__ == "__main__":
    main()
