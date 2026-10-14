# Family 169: completed finite certificate audit

**Version:** 1.0.0. **Source pin:** `1581d4cbdd69a0faf34b2089614fe2a814316a6a`.
**Verified input range:** every naturally labelled h for 0 <= n <= 6.
**Result:** 197/197 graph certificates passed exact independent-code verification.

## Deliverable and significance

This package turns the requested small cases of the permutation-witness identity
into explicit, portable and mutation-tested data. Each witness row names its
actual permitted permutation, its source-defined graph-inversion degree, and an
assigned partition. All raw n-colour monomials and q degrees are retained, so the
claim is stronger than checking graph totals or evaluating q at sample numbers.
The verifier can reconstruct the identity without executing the generator, using
its basis conversion, or assuming the upstream positivity theorem.

The contribution is verification infrastructure and finite certificates, not a
new positivity theorem. The upstream Lean code already contains a finite test
based on colouring and subset-matrix coefficients. Its existence proof and
Encodable.choose-based selection are not replaced or repaired here. The
comparator's sorry is intentional. The paper's packet/wall algorithm and our
coefficient-slot allocation are different constructions.

## Exact verified statement

For each weakly increasing extensive h on [n], n<=6, with edges i<j<=h_i,
let D_G^0 contain exactly the permutations without an adjacent nonedge descent.
The delivered theta_hat assigns a partition of n to each such permutation once.
The full polynomial sum over proper f:[n]->[n], weighted by edge colour ascents,
equals the sum of q^ginv_G(sigma) e_(theta_hat(sigma)) over that domain.

Symmetry was checked before using monomial partitions in the basis conversion.
The conversion used exact rational elimination and integer reconstruction.
The independent checker used direct 0/1 subset-matrix enumeration of elementary
products and compared every coefficient with a fresh brute-force colouring sum.
Integrality, nonnegativity and the degreewise coefficient-count identity passed.

## Full-range results

| n | Graphs | Colour functions examined | Proper colourings | Witness rows | Full monomial/q entries |
|---:|---:|---:|---:|---:|---:|
| 0 | 1 | 1 | 1 | 1 | 1 |
| 1 | 1 | 1 | 1 | 1 | 1 |
| 2 | 2 | 8 | 6 | 3 | 5 |
| 3 | 5 | 135 | 81 | 15 | 51 |
| 4 | 14 | 3,584 | 1,780 | 105 | 655 |
| 5 | 42 | 131,250 | 55,125 | 945 | 9,493 |
| 6 | 132 | 6,158,592 | 2,221,506 | 10,395 | 147,102 |

Totals: **6,293,571** colour functions, **2,278,500** proper colourings,
**100,452** candidate graph/permutation pairs, **11,465** permitted witness rows,
**157,308** nonzero raw coefficients, and **2,207** nonzero elementary/q
coefficients. No isomorphic labelled graphs were identified or discarded.

## Example and boundary behavior

For the three-vertex path h=(2,3,3), the computed expansion is
q e_(2,1)+(1+q+q^2)e_(3). The synthetic map assigns 123 to (3), 132 to (2,1),
213 to (3), and 321 to (3), at degrees 0,1,1,2. The partition assignment within
degree 1 follows our lexicographic rule and is not asserted to be the paper's.
The checker also accepts the alternative that exchanges the two degree-1 shapes.

The empty graph at n=0 has one empty colouring and one empty witness row, both
of weight 1. At n=1 the identity is e_1. The edgeless n=2 regression explicitly
checks four colourings, guarding against accidentally requiring every available
colour to appear.

## Tests and resources

The full suite rejected 792 corrupted inputs. Of these, 195 changed a partition
to another valid partition while simultaneously repairing the redundant summary;
all were rejected by the final full polynomial comparison. There were no
unexpected failures or mathematical mismatches in the completed stages.
The two n<=4/n<=5 baselines remained unchanged. A fresh generation reproduced
all 205 dataset JSON files byte-for-byte.

The original computation stages used 35.555 summed measured wall seconds.
Full n<=6 verification used 11.755 seconds; peak reported child RSS was about
99.4 MiB. The n=5 gate, based on measured runtimes and an eightfold memory
allowance, approved n=6 before it was generated. Detailed values and actual
commands are in the logs and audit/stage_timings.csv. Clean replay components
also passed, but the final mutation step was completed in a separate call after
tool-level interruptions; no uninterrupted driver success is claimed.

## Scope, review and decision

The exact coverage and soundness arguments are in THEOREM_PROOF.md. Its simple
colour-relabeling corollary establishes the identity for every finite alphabet
for each of these same graphs; only n-colour alphabets were enumerated. No graph
with n>6 was attempted. Neither the paper's general proof nor its individual map
was audited in full, and there is no Lean verification claim for this artifact.
The separate checker was written in the same session, not by an independent
reviewer. Only CPython 3.13.5 on Linux was executed; Atlas/macOS remains a replay
target rather than an already tested platform.

No equivalent executable atlas was located in the documented bounded search.
Existing Lean finite tests and Sage's computational functions are acknowledged.
The inaccessible Actions-artifact listing, nonexhaustive fork coverage and
possible unindexed work prevent any novelty conclusion.

**Decision:** hand off this fixed version for independent Atlas replay and review
of the checker/specification correspondence. Preserve the bounded scope; this
work does not justify claiming a new general proof or publication readiness.

## Closing robustness check

A further full-range verification passed under Python `-O` and `--skip-basis`.
All acceptance conditions remain active with assertions disabled, and no basis
data were read. This run used 15.215 measured stage seconds
and raised the maximum recorded child RSS across all runs to 106.8 MiB.
