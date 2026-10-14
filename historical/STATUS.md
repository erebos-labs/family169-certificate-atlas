# Status, v1.0.0

## Established by the exact finite computation

All 197 inputs for 0 <= n <= 6 have an explicit partition-valued permitted-
permutation table. Their full n-colour polynomial identities passed a separate
exact verifier. Colour symmetry was checked rather than imposed; the elementary
coefficients are integral and nonnegative and their sums equal the degreewise
permutation counts. All seven transition matrices and inverses were separately
audited. The mathematical all-finite-alphabet consequence for these same graphs
is proved in THEOREM_PROOF.md, Section 9; only n-colour alphabets were enumerated.

## Independently implemented and actually run

Generator and verifier use different constructions for the h universe,
permutations, colouring enumeration, e-product expansion, and matrix arithmetic.
The core verifier does not import the generator. All 792 negative mutations
were rejected. The two unique-partition boundary cases are explicitly excluded
from the different-valid-partition mutation count. Six positive regressions
passed. A new dataset was generated and all 205 JSON files match byte-for-byte;
its verification and mutation stages completed in separate tool calls.

## Not independently reviewed or formally verified

No separate worker, human referee, or external reviewer checked this work. Both
implementations were written by the same assistant. No Lean file was compiled,
no new Lean theorem is delivered, and the upstream theorem's transitive axioms
and import closure were not audited. This is not a claim that the full paper's
proof or individual algorithm has been independently verified.

## Publication and originality

No equivalent executable atlas was located in the bounded search. This is not a
novelty or priority claim. Upstream Lean already provides a finite coefficient
Test and a selected successful table; Sage already provides chromatic-function
computation and basis tools. The contribution here is the explicit finite data,
separate checker, documented normalization and mutation-tested handoff.
No public release, remote mutation, PR, issue or external communication occurred.
Publication is not authorized by this preparation.

## Remaining unverified scope

Nothing was computed for n>6. The manuscript's packet/wall assignment and Lean's
Encodable.choose-selected assignment were not evaluated or compared to ours.
No unrestricted enumeration, wall construction, scattering algorithm or new
general proof was attempted. No elementary-unimodality claim is made.
macOS/Atlas was not used for execution. An uninterrupted run of replay.py was
not completed because the tool interrupted both monolithic attempts; the exact
component stages and final file comparison did complete. The interrupted logs
are retained and labelled. CI artifact listings were inaccessible through the
available GitHub endpoint, and forks/unindexed work were not exhaustively audited.

## Next decision

Hand this fixed version to an independent Atlas run and a reviewer of the small
checker/specification correspondence. Do not enlarge n, formalize the general
paper, or describe this as new general positivity on the strength of these tests.

The supplementary full check under Python -O with --skip-basis also passed
all 197 graphs. Its actual output and metrics are included.
