# Source and convention audit

## Provenance and inspection scope

The source pin throughout is openai/math commit
1581d4cbdd69a0faf34b2089614fe2a814316a6a. All six requested files were accessible
through the read-only GitHub connector and were read before implementation.
The additional graph-convention, completion and actual Lean Model files were
read to settle the change of convention and distinguish the comparator from the
solution. Full paths, URLs and available upstream Git blob identifiers are in
source_manifest.json. Long TeX responses were expanded to read their remaining
content, not treated as complete merely because an initial response was truncated.

The original manuscript and Lean files were not copied into this archive. They
remain identified by immutable repository paths and the full source commit.
The delivered checker is offline and does not need to download them. The only
vendored upstream file is the Apache-2.0 license text, whose bytes match its Git
blob identifier. The audit below is an authored description, not a claim that
all upstream dependencies or bibliography references were fully verified.

## Original problem and target

S1 (01-introduction.tex), labels main:csf, main:theorem and main:witness, defines
weakly increasing extensive h on [n], edges i<j<=h_i, proper colourings weighted
by COLOUR ASCENTS, and D_G^0 consisting of permutations with adjacent descents
allowed only on graph edges. ginv_G counts inversions on all edge-supported
position pairs. The theorem's theta is partition-valued and has an identity
uniform in the colour alphabet. The source does not assert e-unimodality.

S3 (the comparator) and S9 (the actual Model.lean) give these same definitions
using Fin n. The translation used here is exactly

    paper vertex i       <-> Lean value i-1,
    paper h_i            <-> Lean (G.h (i-1)).val + 1,
    colour index c+1     <-> Python/Lean finite index c,
    permutation letter i <-> Lean value i-1.

Monotonicity and extensivity are unchanged by this shift. Our graph endpoints
and h in the certificate remain 1-based. Only Python's internal array indexing
and the indexing of the exponent-vector entries start at zero. The first
exponent coordinate always denotes x_1. No graph labelling is canonicalized.

The finite colour alphabet has exactly n AVAILABLE colours. A function is not
required to hit every colour. This matches the comparator's sum over all proper
functions Fin n -> Fin r at r=n. Requiring surjectivity would silently change the
problem and would already fail the edgeless two-vertex regression.

## Internal manuscript convention and its reversal

S2 (06-witness.tex), especially route:masks, route:word-energy and route:algorithm,
works first on an internal domain A_G which forbids adjacent NONEDGE ASCENTS.
Its required masks record increasing adjacent nonedges, and exact-empty masks
define its admissible input words. This is not D_G^0 directly. The section records
centered energy E(w)=2 inv_G(w)-M and constructs Lambda_G(w) by finite packet
switches, common histories, return to anchors and exact-mask cancellation.
The finite slot assignment in this deliverable does not execute those operations.

S7 (02-graphs.tex), Lemma label graph:digits and equation graph:reverse, gives

    reverse : D_G^0 -> A_G,
    inv_G(reverse sigma) = M - ginv_G(sigma).

This follows directly: reversal exchanges adjacent descents and ascents, without
changing which letter pairs are edges, and reverses the position order of the two
endpoints of every edge. Both implementations check this domain correspondence
and complementary-degree relation while enumerating every permutation. They do
NOT relabel the vertices or silently replace the requested domain by A_G.

S7 uses an intermediate colouring function X_G with COLOUR INVERSIONS.
Lemma graph:reciprocity shows X_G=chi_G and shape reciprocity by reversing the
finite colour alphabet and using symmetry. S8 (07-completion.tex) then returns
to the introduction's convention by defining

    theta_G(sigma)=Lambda_G(reverse sigma)

and applying q^M c_lambda(q^-1)=c_lambda(q). These two distinct reversals are the
reason one should not copy the internal domain or energy directly into the
introduction's witness statement. Our core computations use the introduction's
colour ascents and D_G^0 from the start; no reciprocity theorem is assumed in
acceptance. The additional raw coefficient reversal check is independently
recomputed from colourings.

## What the actual Lean solution already supplies

S3 ends with the comparator declaration of elementaryPositivityWitness proved by
an intentional sorry. It is the challenge statement, not the implementation.
No repair or defect claim is based on that placeholder.

S4 (HistoryMainWitness.lean) defines a noncomputable historyWitness via the
admissible partition and its polynomial expansion. It also already introduces
an exact finite coefficient-test framework:

- Row n: n bounded nonnegative entries summing to n, converted to a partition;
- WordOK: bijectivity and the original adjacent-descent condition;
- wordEnergy: the original graph-inversion count;
- colorCount: proper n-colour functions at a full exponent vector and q degree;
- matrixCount: ordered subset rows with prescribed row and column sums;
- witnessCount: word contributions weighted by those subset-matrix counts;
- Test: equality for all bounded exponent vectors and degrees through edgeCount.

Its matrix_coefficient, chromatic_coefficient and witness_coefficient lemmas
connect those finite counts to the polynomial definitions. Thus a finite
coefficient test is a pre-existing idea in this exact family, not an invention
of the atlas. Our independent checker realizes direct finite coefficient
verification in small executable Python, without importing these lemmas.

S5 (ElementaryAlphabetRigidity.lean) proves expansion_of_test and algebraic
injectivity/uniformity statements. Importantly, uniform_expansion_of_test takes
an EXISTING W:G.PermutationWitness, and exists_test also uses W. We do not present
that theorem as a positivity-independent proof that an arbitrary finite test
extends to all colours. Our standalone all-alphabet argument is given separately
in THEOREM_PROOF.md, Section 9, using increasing colour relabeling only.

S6 (Main.lean) supplies the actual top-level solution. Its sequence is

    exists_successful_table := exists_test G G.historyWitness
    selectedTable := Encodable.choose (exists_successful_table G)
    selectedTable_test := Encodable.choose_spec ...
    elementaryPositivityWitness.theta := rowPartition (selectedTable G sigma)

with the uniform expansion justified using the history witness and finite test.
These declarations were inspected; they were not executed, compiled or subjected
to a complete transitive axiom audit in this session. The selected table is not
assumed equal to the atlas's table.

## Relation of the certificate encoding to Lean's finite test

Lean's table is defined on all words Fin n -> Fin n, whereas our certificate
stores only the WordOK/permutation rows that contribute to witnessCount. Values
on other words have zero contribution and may be filled arbitrarily. A partition
can be padded with zero rows to obtain a Row n; every zero row has only the empty
subset choice. Removing such rows does not change matrixCount. Permuting its
nonzero rows only permutes labelled subset choices, preserving their column sums.
Thus our positive-part partition representation computes the same elementary
product coefficient, without attempting to encode Lean's selected table.

Lean's Test permits all alpha coordinates in 0,...,n. Our sparse data retains
only sum(alpha)=n, because both the colouring polynomial and every witness term
are homogeneous of degree n. Our direct verification argument checks that bound,
and all coefficients outside it are zero. Both definitions also have q degree
at most the number of graph edges. No testing region has been silently omitted.

## Three-vertex path cross-check

S1, equation label main:path-example, gives

    chi_path = q e_(2,1) + (1+q+q^2)e_(3),
    D_G^0 = {123,132,213,321}, with degrees {0,1,1,2}.

The raw colouring coefficients, exact elementary conversion, permitted domain
and graph-inversion degrees all reproduce this example. Our lexicographic
allocation gives (2,1) to 132. The introductory equation alone does not choose
between 132 and 213, and no claim is made that our choice agrees with the
manuscript's packet procedure.

## Audit conclusion and dependency limits

The requested finite specification matches the original natural labels,
colour-ascent convention, permitted-descent domain and graph-inversion degrees.
No symmetry, quotient, coefficient invariance, surjectivity, or stronger graph
assumption was introduced. Symmetry is a checked output.

Only the definitions and explicit finite algebra/coverage reasoning are needed
for the delivered computation. The mathematical correctness of all wall,
shuffle, triangular, history and cancellation dependencies in the general
upstream proof remains outside this audit. No new formal-verification or
novelty claim follows from inspecting their top-level references.
