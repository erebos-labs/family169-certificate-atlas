"""Third implementation: ordered set partitions and constrained row recurrence.

Imports no packaged mathematical code. Normal Python assertions are mandatory.
"""
import argparse
from collections import Counter
from functools import cache
from itertools import product, permutations, combinations
from math import factorial, comb
from pathlib import Path
import hashlib
import json
import platform
import sys
import time


def set_partitions(n):
    if n == 0:
        yield ()
        return
    def rec(word, top):
        if len(word) == n:
            yield tuple(word)
        else:
            for b in range(top + 2):
                yield from rec(word + [b], max(top, b))
    yield from rec([0], 0)


@cache
def ordered_blocks(n):
    out = []
    for p in set_partitions(n):
        k = max(p, default=-1) + 1
        for order in permutations(range(k)):
            ranks = {block: rank for rank, block in enumerate(order)}
            word = tuple(ranks[b] for b in p)
            alpha = tuple(word.count(j) for j in range(k))
            out.append((word, alpha))
    # Every packed colouring has exactly one unordered partition and block order.
    assert len({w for w, a in out}) == len(out)
    assert sum(comb(n, len(a)) for w, a in out) == n**n
    return out


def polynomial(n, edges, r):
    out = Counter()
    packed_count = 0
    for word, packed in ordered_blocks(n):
        if any(word[i] == word[j] for i, j in edges):
            continue
        packed_count += 1
        d = sum(word[i] < word[j] for i, j in edges)
        # Each strictly increasing choice of occupied colours lifts the packed word.
        for occupied in combinations(range(r), len(packed)):
            a = [0] * r
            for c, count in zip(occupied, packed):
                a[c] = count
            out[tuple(a), d] += 1
    return out, packed_count


@cache
def elementary_coefficient(lam, alpha):
    # Count labelled rows by residual column capacities; no mask matrices or
    # precomputed polynomial convolution. Equal-length rows remain distinct.
    if not lam:
        return int(not any(alpha))
    k = lam[0]
    if sum(alpha) != sum(lam) or max(alpha, default=0) > len(lam):
        return 0
    total = 0
    for cols in combinations([i for i, x in enumerate(alpha) if x], k):
        rem = list(alpha)
        for i in cols:
            rem[i] -= 1
        total += elementary_coefficient(lam[1:], tuple(rem))
    return total


def compositions(n, r):
    if r == 0:
        if n == 0:
            yield ()
        return
    for first in range(n + 1):
        for rest in compositions(n - first, r - 1):
            yield (first,) + rest


def permutation_insertions(n):
    words = [()]
    for label in range(1, n + 1):
        words = [w[:j] + (label,) + w[j:] for w in words for j in range(label)]
    assert len(words) == factorial(n) == len(set(words))
    return words


def determinant(matrix):
    # Leibniz sum via subset DP, independent of rational/Bareiss elimination.
    dp = {0: 1}
    size = len(matrix)
    for row in range(size):
        nxt = Counter()
        for used, coefficient in dp.items():
            for col in range(size):
                if not (used >> col) & 1:
                    greater = (used >> (col + 1)).bit_count()
                    nxt[used | (1 << col)] += coefficient * matrix[row][col] * (-1)**greater
        dp = nxt
    return dp[(1 << size) - 1]


def audit(root):
    assert __debug__, 'Independent audit requires ordinary assertion execution'
    start = time.perf_counter()
    atlas = root / 'atlas'
    catalog = json.loads((atlas / 'atlas.json').read_text())
    assert catalog['min_n'] == 0 and catalog['max_n'] == 6
    records = {(o['n'], tuple(o['h'])): o for o in catalog['graphs']}
    universe = {(n, h) for n in range(7) for h in product(range(1, n + 1), repeat=n)
                if all(h[i] >= i + 1 and (i == 0 or h[i] >= h[i-1]) for i in range(n))}
    assert len(records) == len(catalog['graphs']) == 197
    assert set(records) == universe
    rows = []
    for n, h in sorted(universe):
        rec = records[n, h]
        path = atlas / rec['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == rec['sha256']
        obj = json.loads(path.read_text())
        assert obj['n'] == n and obj['h'] == list(h)
        edges = [(i, j) for i in range(n) for j in range(i + 1, n) if j < h[i]]
        assert obj['edges'] == [[i+1, j+1] for i, j in edges]
        es = {frozenset((i+1, j+1)) for i, j in edges}
        domain = {}
        for w in permutation_insertions(n):
            if any(a > b and frozenset((a, b)) not in es for a, b in zip(w, w[1:])):
                continue
            d = sum(w[i] > w[j] and frozenset((w[i], w[j])) in es
                    for i in range(n) for j in range(i+1, n))
            domain[w] = d
        got = {tuple(x['permutation']): x for x in obj['witness']}
        assert len(got) == len(obj['witness']) == len(domain) and set(got) == set(domain)
        bins = Counter()
        for w, x in got.items():
            lam = tuple(x['partition'])
            assert x['degree'] == domain[w]
            assert all(type(v) is int and v > 0 for v in lam)
            assert lam == tuple(sorted(lam, reverse=True)) and sum(lam) == n
            bins[lam, domain[w]] += 1
        summary = {(tuple(x['partition']), d): c for x in obj['elementary']
                   for d, c in enumerate(x['q_coefficients']) if c}
        assert dict(bins) == summary
        # Also verify the declared deterministic lexicographic allocation rule.
        for d in range(len(edges) + 1):
            pool = sorted(w for w, degree in domain.items() if d == degree)
            slots = sorted(lam for (lam, degree), count in bins.items() if degree == d for _ in range(count))
            assert [tuple(got[w]['partition']) for w in pool] == slots
        raw, packed = polynomial(n, edges, n)
        recorded = {(tuple(x['alpha']), x['degree']): x['coefficient'] for x in obj['monomials']}
        assert len(recorded) == len(obj['monomials']) and recorded == dict(raw)
        rhs = {}
        for alpha in compositions(n, n):
            for d in range(len(edges) + 1):
                c = sum(count * elementary_coefficient(lam, alpha)
                        for (lam, degree), count in bins.items() if degree == d)
                if c:
                    rhs[alpha, d] = c
        assert rhs == dict(raw)
        stat = {'n': n, 'h': list(h), 'graphs': 1, 'colour_candidates': n**n,
                'proper_colourings': sum(raw.values()), 'packed_proper_colourings': packed,
                'permutation_candidates': factorial(n), 'witness_rows': len(got),
                'raw_coefficients': len(raw), 'elementary_coefficients': len(bins)}
        rows.append(stat)
        print(json.dumps({'event':'independent_graph_pass', **stat}), flush=True)
    basis = []
    for n in range(7):
        ps = sorted({tuple(x for x in a if x) for a in compositions(n, n)
                     if a == tuple(sorted(a, reverse=True))})
        b = json.loads((atlas / 'basis' / f'n{n:02d}.json').read_text())
        assert b['partitions'] == [list(p) for p in ps]
        reps = [p + (0,) * (n-len(p)) for p in ps]
        mat = [[elementary_coefficient(p, a) for p in ps] for a in reps]
        assert b['matrix_rows_mu_columns_lambda'] == mat
        assert b['representatives'] == [list(a) for a in reps]
        inv = b['inverse_rows_lambda_columns_mu']
        assert all(sum(mat[i][k]*inv[k][j] for k in range(len(ps))) == int(i==j)
                   for i in range(len(ps)) for j in range(len(ps)))
        det = determinant(mat)
        assert b['determinant'] == det and abs(det) == 1
        basis.append({'n':n,'dimension':len(ps),'determinant':det})
    totals = {k:sum(r[k] for r in rows) for k in rows[0] if k not in {'n','h'}}
    return {'event':'independent_audit_pass', 'methods':['ordered_set_partitions','residual_column_recurrence','insertion_permutations','subset_dp_determinant'],
            'totals':totals,'by_n':[{k:sum(r[k] for r in rows if r['n']==n) for k in totals} | {'n':n} for n in range(7)],
            'basis':basis,'seconds':time.perf_counter()-start,'python':sys.version,'platform':platform.platform()}


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('root',type=Path)
    ap.add_argument('--result',type=Path,required=True)
    a = ap.parse_args()
    result = audit(a.root)
    a.result.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result),flush=True)
