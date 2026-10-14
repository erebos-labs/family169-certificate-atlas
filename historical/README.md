# Family 169 finite certificate atlas, v1.0.0

**Result: all 197 naturally labelled graphs with 0 <= n <= 6 passed exact verification.**
The package contains 197 graph certificates, 11,465 explicitly assigned permitted
permutations, and 157,308 nonzero full-monomial/q-degree coefficients. The verifier
re-enumerates colourings and permutations and expands elementary products directly.
It does not call a positivity theorem or trust the generator's change of basis.

Upstream specification: `openai/math`, commit `1581d4cbdd69a0faf34b2089614fe2a814316a6a`,
family 169, *Elementary positivity of chromatic quasisymmetric functions*.

This is a **synthetic finite witness atlas**, obtained by allocating permutations
according to independently computed elementary coefficient counts. It is not the
paper's packet/wall map, not Lean's `Encodable.choose`-selected table, not a new
general proof, and not a claim of mathematical or software priority. The existing
Lean finite-test design is explicitly acknowledged in `audit/SOURCE_AUDIT.md`.

## Verify on Atlas, offline

Extract the ZIP and enter `family169_atlas_v1.0.0`. Use Python 3.10 or newer;
CPython 3.13.5 on Linux is the environment actually tested. No packages need to be
installed. macOS/Atlas itself has not been tested in this session.

```sh
python3 src/check_hashes.py
python3 src/verify.py --atlas atlas
python3 src/mutation_tests.py --atlas atlas
```

`verify.py` exits unsuccessfully on a mismatch. It checks the complete graph
catalogue, all certificate hashes, the actual permitted-permutation domain, the
recorded graph-inversion degrees, every raw colouring coefficient, symmetry,
and every coefficient in the expanded witness identity. The optional independent
basis audit runs after the core checks, and is not used to accept a witness.
To demonstrate the core check without reading any basis file:

```sh
python3 src/verify.py --atlas atlas --skip-basis
```

For a clean staged regeneration, choose a directory which does not already exist:

```sh
python3 src/replay.py --output ../family169-replay
```

This runs n <= 4 and its regressions first, measures n = 5, applies the documented
resource gate, and only then attempts n = 6. It compares all 205 resulting JSON
files byte-for-byte with the packaged atlas. It will refuse an existing output
directory, stops at n = 5 when its resource gate fails, and hard-caps n at 6.
The stage components and byte identity were successfully tested; two all-in-one
replay invocations were interrupted by the interactive tool's outer timeout during
mutation tests. The final clean replay was completed in separate tool calls.
An uninterrupted end-to-end execution of the driver is **not** claimed.

The Linux wrapper applies a 2,000,000,000-byte address-space limit to each child.
On macOS it records RSS but does not apply that Linux-specific limit. The replay
gate still uses the measured RSS and remaining time. See `audit/RESOURCE_AUDIT.md`.

## Exact scope

For every weakly increasing h = (h_1,...,h_n) with i <= h_i <= n, on the natural
labels 1,...,n, an edge is an unordered pair {i,j} with i < j <= h_i. No graph
isomorphism quotient or relabelling is used. A colouring has n **available** colours;
it is not required to use every colour. Ascents use the increasing natural vertex
order. An adjacent permutation descent is permitted exactly when its two letters
are adjacent in the graph; graph inversions count all inverted edges, not only
adjacent letters.

The directly checked identity is

    sum_(proper f:[n]->[n]) q^asc_G(f) prod_i x_(f(i))
       = sum_(sigma in D_G^0) q^ginv_G(sigma) e_(theta_hat_G(sigma))(x_1,...,x_n).

All arithmetic is integer or exact rational arithmetic. No floating-point
coefficient calculation is used. Missing sparse coefficients mean zero, not
unexamined entries. The complete justification of coverage and the elementary
basis calculation is in `THEOREM_PROOF.md`.

A short order-preserving colour-relabeling argument extends the checked identity
for each of these fixed graphs to every finite alphabet. That argument is supplied
in `THEOREM_PROOF.md`; alphabets other than n were not exhaustively enumerated.
Nothing is established here for graphs with n > 6.

## Counts from the actual full verifier run

| n | Graphs | Colour functions examined | Proper colourings | Permitted permutations | Nonzero monomial/q entries |
|---:|---:|---:|---:|---:|---:|
| 0 | 1 | 1 | 1 | 1 | 1 |
| 1 | 1 | 1 | 1 | 1 | 1 |
| 2 | 2 | 8 | 6 | 3 | 5 |
| 3 | 5 | 135 | 81 | 15 | 51 |
| 4 | 14 | 3,584 | 1,780 | 105 | 655 |
| 5 | 42 | 131,250 | 55,125 | 945 | 9,493 |
| 6 | 132 | 6,158,592 | 2,221,506 | 10,395 | 147,102 |
| **Total** | **197** | **6,293,571** | **2,278,500** | **11,465** | **157,308** |

Across these graphs, the verifier enumerated 100,452 graph/permutation pairs
before applying the permitted-domain filter. All 2,207 nonzero elementary
partition/q-degree coefficients are nonnegative integers. The numbers are sums
over labelled graph instances, not counts after identifying isomorphic graphs.

## Tests, measurements and reproducibility

The original eight completed computation stages used **35.555 seconds** of summed
measured child-stage wall time. Full verification of n <= 6, including the separate
basis audit, used **11.755 seconds**. The maximum reported child RSS was
**104,214,528 bytes** (about 99.4 MiB). These are observations on the recorded Linux
environment, not promises about another computer.

The mutation suite rejected **792 corrupted inputs**. Changing to a different
valid partition is inapplicable only for n = 0 and n = 1, which each have one
partition; those two cases are recorded as inapplicable, not passed tests.
Six positive regressions include both boundary cases, the two graphs on two
vertices, the paper's three-vertex path, and a valid alternative path witness.

A clean regeneration reproduced **all 205 JSON files byte-for-byte**, including
certificates, basis data and the catalogue. Its final mutation test completed in
a separate call after outer-tool interruptions. Original n <= 4 and n <= 5 data
were preserved unchanged; snapshots and 99 baseline-file hash comparisons are
included. Neither partial replay log is presented as a completed test run.

## Package guide

`REPORT.md` gives the main findings and limitations. `STATUS.md` separates exact
checks, review and formalization status. `THEOREM_PROOF.md` explains the finite
mathematics and checker coverage. `audit/` contains source conventions, bounded
prior-work search, resource and mutation audits, environment data, CSV counts and
source metadata. `src/` contains the six standard-library programs.
`atlas/certificates/` contains the graph witnesses and raw coefficient tables;
`atlas/basis/` contains seven exact transition matrices and inverses.
`baselines/` preserves the smaller stages. `logs/` contains actual outputs,
metrics and clearly labelled interrupted attempts. `RESULTS.json` is the
machine-readable summary; `SHA256SUMS` covers the packaged files.

## What this does not certify

No new Lean theorem was compiled. The upstream Lean import closure and axioms were
not audited. The generator and distinct checker were written in the same session;
there was no independent human, worker or referee review. Python, its standard
library and the runtime remain in the computational trust base. The whole paper's
wall/scattering proof was not validated, and the synthesized assignments do not
certify its individual-input algorithm. No equivalent atlas was located in the
bounded search, but this does not establish novelty.

All supplied work is a private research handoff for Erebos Labs. No publication,
issue, pull request, message to contributors or remote mutation was performed.
See `LICENSE` and `NOTICE` for licensing and attribution.

### Additional closing check

All 197 graphs also passed `python -O` with `--skip-basis`, confirming that the
core checks do not rely on Python assertions or the basis files. Its recorded
peak child RSS was 112,005,120 bytes (about 106.8 MiB), the
maximum across all recorded completed runs, not just the original eight stages.
