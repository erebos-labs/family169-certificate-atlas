# Independent Atlas audit of family169 certificate atlas v1.0.0

**Recommendation: ready for finite-package publication within the stated scope.**
No mathematical mismatch, enumeration gap, or acceptance bug was found. This is
an independently checked finite synthesized-witness package for every naturally
labelled input with 0 <= n <= 6. It does not validate the paper's individual map,
the general theorem, or a Lean proof. Publication itself was not performed.

## Original and audit isolation

The requested ZIP was retrieved from ChatGPT Library using its supported
materialization route and current transfer helper. The original is preserved at
`originals/family169_certificate_atlas_v1.0.0.zip`. Its size is 880881 bytes and
its independently recomputed SHA-256 is:

`f8d5741320af26b7485c531c57075104ccd07213953f09c2e413480f752354a8`.

This agrees with the Library checksum sidecar. The separately read Library
REPORT.md and THEOREM_PROOF.md have the same content as the ZIP documents.
All 295 archive paths were inspected before extraction: no absolute paths,
parent traversal, backslash paths, or symlinks were present; expanded size was
9934950 bytes. The scripts were read before execution and use standard-library
finite arithmetic and bounded subprocess replay. No applicable AGENTS.md was
found in the audit directory's ancestor chain.

The audit directory is
`AUDIT_WORKSPACE`.
The ZIP's 294 manifest-covered files match SHA256SUMS, and the manifest's file
set is exact, excluding SHA256SUMS itself. Both packaged baselines match their
28 and 71 checksums. Original ZIP and manifest-covered files were rechecked
after execution and remain unchanged. Python bytecode caches created during
replay are additional runtime files, not modifications to source or data.

## Correspondence with authoritative sources

Nine files were retrieved read-only at openai/math commit
`1581d4cbdd69a0faf34b2089614fe2a814316a6a` and saved with exact bytes in
`upstream/`. Every one of the eight available expected Git blob identifiers
matches independently. `upstream/source-verification.json` records paths,
immutable URLs, byte counts, SHA-256 and Git blob SHA-1.

The introduction, Comparator and actual Model.lean agree: h is weakly increasing
and extensive; edges are i < j <= h_i; the colouring exponent counts colour
ascents along increasing natural labels. The domain forbids adjacent NONEDGE
DESCENTS. Graph inversions count all inverted graph edges, not merely adjacent
letters. Translating Fin n values to 1-based labels adds one to vertices and h;
no vertex relabelling or graph-isomorphism quotient is involved.

The manuscript's internal A_G instead forbids nonedge ascents. Word reversal
maps D_G^0 to A_G and complements the degree. Completion sets theta(sigma) to
Lambda(reverse sigma), and colour reciprocity explains the final grading.
The delivered calculations use the introduction's conventions directly.

HistoryMainWitness already defines a finite coefficient test using proper
colourings and labelled subset rows. Main.lean chooses a successful table via
Encodable.choose, after existence is supplied by historyWitness. The atlas's
lexicographic coefficient-slot allocation is distinct from this choice and
from the paper's packet/wall construction, which does not take final elementary
coefficients as input. Agreement of identities does not identify their tables.
The comparator's sorry is the challenge statement, not a reported solution bug.

## Complete bounded replay

Atlas was macOS 26.6.2, arm64, CPython 3.14.7. The inspected driver ran once,
uninterrupted, with a 600-second aggregate budget and a fresh `replay-v1/`.
Its gate permitted n=6. All stages completed, including normal Python verification
with the full basis audit and all mutation tests. The final driver event is
`replay_pass`: 197 graphs and all 205 dataset JSON files reproduced byte-for-byte.
Elapsed driver wall time was 22.461 seconds; measured child-stage wall time was
21.993 seconds and maximum reported child RSS was 31440896 bytes. No timeout
occurred. macOS does not apply the Linux address-space limit; the finite scope,
runtime caps and measured resource gate remained active.

This closes the original report's explicit gap about an uninterrupted driver and
Atlas execution. Exact evidence: `logs/full-driver.log`,
`replay-v1/replay_summary.json`, and `replay-v1/logs/`.

## Third mathematical implementation

`independent_audit.py` imports neither supplied generator nor verifier. It:

- Constructs the full h universe from Cartesian tuples and filters it, and
  compares it with the exact 197 catalogue records.
- Enumerates colourings through unordered set partitions, orders their blocks,
  and lifts each packed colouring to every increasing choice of occupied colours.
  Uniqueness and the total n^n coverage of these lifts are checked independently.
- Constructs all permutations by inserting successive largest letters, filters
  the specified descent domain, and recomputes all graph-inversion degrees.
- Checks that certificate rows cover this domain exactly once, validates every
  partition and degree, and checks the claimed lexicographic slot assignment.
- Counts elementary coefficients through a recurrence on residual column
  capacities, checks every weak composition and every degree 0 through M, and
  compares the whole sparse polynomial identity with freshly counted colourings.
- Rebuilds all seven transition matrices, checks their integer inverses, and
  computes their determinants using a Leibniz subset dynamic program.

All 197 graphs passed, in 1.722 seconds. The confirmed totals are 6293571 colour
functions covered, 2278500 proper colourings, 100452 candidate permutation/graph
pairs, 11465 permitted witness rows, 157308 nonzero raw coefficients and 2207
nonzero elementary/degree coefficients. The graph counts by n are
1,1,2,5,14,42,132. Matrix dimensions are 1,1,2,3,5,7,11, with determinants
1,1,-1,-1,1,-1,-1. Detailed totals are in `independent-results.json` and every
graph acceptance is in `logs/independent.log`.

At n=0 the colouring, permutation and partition are empty and both sides are 1;
at n=1 the identity is e_1. Edgeless n=2 retains four colourings, including those
that omit an available colour. For path3 the domain is 123,132,213,321 with
degrees 0,1,1,2, and the expansion is q e_(2,1)+(1+q+q^2)e_3. The raw coefficient
of x_1 x_2 x_3 is 1+4q+q^2; each permutation of (2,1,0) has coefficient q.
These agree with the pinned introduction. Exchanging the two degree-one shapes
is correctly accepted as another valid finite witness.

The proof's extension to other finite alphabets for these SAME graphs is sound:
each degree-n monomial occupies at most n colours; order-preserving packing
preserves equality and strict comparisons on both colouring and subset sides.
Both coefficients are therefore among those checked in n colours. At r=0,
positive degree vanishes, while degree zero is 1. This argument proves no claim
for graphs larger than six and requires no upstream positivity theorem.

## Corruption and optimized execution

The full supplied suite rejected all 792 corrupted inputs under ordinary Python,
including 195 valid-partition changes with their redundant summaries repaired.
It also rejected all 792 under Python -O. Two different-partition mutations are
correctly inapplicable at n=0 and n=1. Six positive regressions pass.

Additional external CLI probes made new audit copies and repaired catalogue
hashes before testing semantic corruptions. Both normal and optimized execution
reject consistent wrong shapes, reversed inversion degrees, a forbidden nonedge
descent, a boolean degree, a missing raw term, and corrupted basis matrix,
inverse and determinant. Sixteen CLI rejections and one third-implementation
rejection are recorded in `additional-probes.json`; exact CLI diagnostics are
in `logs/probe-*.log`. Both skip-basis runs intentionally accept irrelevant basis
corruption, demonstrating the core witness check's independence from basis data.

Separately, the full optimized core run accepted all 197 original graphs with
--skip-basis in 8.049 seconds. Inspection confirms that supplied acceptance
conditions use explicit errors rather than Python assertions. Optimized success
alone is not evidence about the basis; the ordinary full replay and third
implementation independently validate that data. Evidence is in
`logs/optimized-core.*` and `logs/optimized-mutations.*`.

## Limits and next release

No blocker remains for this finite package. This review establishes neither a
new general theorem nor novelty. It does not compute the paper's particular map,
audit the full manuscript, compile Lean, or inspect Lean's transitive axiom
closure. The computational trust base includes Python and the operating system;
the checker is not kernel-certified. These are scope limits, not discovered bugs.

For a publication release, attach this independent audit and update historical
status text to mention the completed Atlas review and uninterrupted replay.
Keep the finite synthesized-witness framing and existing caveats. No original
package edits, commits, pushes, PRs, publication, or external messages were made.
