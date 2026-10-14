# Family 169 finite certificate atlas

An Erebos Labs release of **synthesized finite permutation witnesses** for
every naturally labelled unit interval graph with **0 <= n <= 6**.

All **197 graphs** have an explicit table assigning a partition to each permitted
permutation, with **11465 witness rows** and **157308 nonzero monomial/q-degree
coefficients**. The supplied checker recomputes the full polynomial identity;
an independently written third implementation also checks every graph and basis
matrix. No third-party mathematical package or numerical tolerance is used.

**Release v1.0.1** adds the completed independent Atlas audit and CI. All 205
dataset JSON files and six original scripts remain byte-identical to the v1.0.0
handoff; the catalogue's dataset version is therefore still 1.0.0.

## Verify locally

Python 3.10 or newer and its standard library suffice. From this repository:

```sh
python3 src/check_hashes.py
python3 src/verify.py --atlas atlas
python3 src/mutation_tests.py --atlas atlas
python3 independent/independent_audit.py . --result /tmp/family169-independent-results.json
```

For a complete staged regeneration, choose a directory that does not exist:

```sh
python3 src/replay.py --output ../family169-replay --budget-seconds 600
```

The driver verifies n<=4, measures n=5, gates n=6 by its resource projection,
runs all normal basis/semantic/mutation checks, and compares all 205 regenerated
JSON files byte-for-byte. Scope is hard-capped at six. On a slower machine a
600-second gate may stop at n=5; the recorded `replay_bounded_stop` is distinct
from a completed `replay_pass`. A budget up to 7200 seconds is supported.

Additional checks use fresh external output directories:

```sh
python3 -O src/verify.py --atlas atlas --skip-basis
python3 -O src/mutation_tests.py --atlas atlas
python3 independent/additional_probes.py . --output ../family169-probes
```

The core witness checker uses explicit error checks, which stay active under
`-O`. Basis validation is separate and runs in the normal full verifier.

## Exact identity and conventions

For a weakly increasing extensive h on natural labels [n], edges are i<j<=h_i.
Proper colourings use n available colours and need not be surjective. The
colouring degree counts edge colour ascents in increasing natural vertex order.
D_G^0 consists of permutations whose adjacent descents occur only on graph
edges; ginv counts all inverted graph edges, including nonadjacent positions.

The finite identity is

```text
sum_(proper f:[n]->[n]) q^asc_G(f) product_i x_(f(i))
  = sum_(sigma in D_G^0) q^ginv_G(sigma) e_(theta_hat_G(sigma)).
```

At n=0 both sides are 1; at n=1 the identity is e_1. For path3 the expansion is
q e_(2,1)+(1+q+q^2)e_3, with domain 123,132,213,321 and degrees 0,1,1,2.
Every full exponent vector and q degree is checked. Missing sparse entries mean
zero. [THEOREM_PROOF.md](THEOREM_PROOF.md) explains the coverage, arithmetic and
order-preserving colour-packing argument extending each fixed graph's identity
to every finite alphabet; no graph larger than six is included.

## Independent audit and reproducibility

The independent Atlas audit passed on macOS arm64 with CPython 3.14.7. One
uninterrupted full driver finished in 22.461 seconds and reproduced all 205
dataset JSON files. A third implementation checks colourings through ordered set
partitions, elementary coefficients through residual column capacities,
permutations through insertion, and determinants through subset dynamic
programming. It confirms 2278500 proper colourings and 2207 nonzero
elementary/q-degree coefficients. All 792 supplied corruptions are rejected
under normal Python and `-O`; additional probes test semantic corruptions after
repairing catalogue hashes, plus matrix/inverse/determinant corruption.

Read [the independent review](independent/REVIEW.md),
[audit results](independent/AUDIT_RESULTS.json), and [current status](STATUS.md).
[GitHub Actions](https://github.com/erebos-labs/family169-certificate-atlas/actions)
runs complete replay and independent checks on Linux and macOS.

## Scope, antecedents and attribution

The specification is [openai/math family 169](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/docs/169.md),
*Elementary positivity of chromatic quasisymmetric functions*, pinned at
1581d4cbdd69a0faf34b2089614fe2a814316a6a. Its paper and Lean definitions were
checked for correspondence. Upstream Lean already supplies a finite coefficient
Test and an existentially selected successful table; SageMath already supplies
chromatic-function computation and symmetric-basis tools.

This atlas assigns coefficient slots to permutations in lexicographic order.
It does **not** execute the paper's packet/wall map or reproduce Lean's
Encodable.choose-selected table. It establishes no new general theorem,
novelty, priority, elementary unimodality, or n>6 result. No Lean compilation,
transitive axiom audit, human referee review, or kernel certification is claimed.
Implementation and independent agent review were AI-assisted.

The software, generated certificates and notes are Apache-2.0; see [LICENSE](LICENSE)
and [NOTICE](NOTICE). Historical v1.0.0 documents remain unchanged in
[historical/](historical/); their missing-review and missing-Atlas statements refer
to the earlier handoff. Public log copies replace absolute runtime paths with
symbolic labels. [PROVENANCE.json](PROVENANCE.json) records exact preservation
and public packaging changes. Original private artifacts remain preserved locally.

## Package layout

- `atlas/`: catalogue, 197 certificates and seven basis datasets.
- `src/`: original generator, verifier, mutations, resource wrapper and replay.
- `independent/`: independent checker, review, probe CLI and public audit evidence.
- `audit/`, `baselines/`, `logs/`: source conventions and original bounded evidence.
- `historical/`: unchanged original handoff documents and original manifest.
- `SHA256SUMS`: hashes of this public release tree.
- `tools/package_release.py`: deterministic release asset builder.
