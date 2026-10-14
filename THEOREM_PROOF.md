# Exact finite statement and verification argument

## 1. Definitions, assumptions and quantifiers

Fix an integer n with 0 <= n <= 6. Let H_n be the set of tuples
h = (h_1,...,h_n) of integers such that h_i <= h_(i+1) whenever i < n and
 i <= h_i <= n for every i in [n] = {1,...,n}. The only member of H_0 is ().
Let G(h) have vertex set [n] and unordered edges {i,j} with i < j <= h_i.
Labels are part of the input and remain fixed throughout.

For a finite alphabet [r], a proper colouring is any function f:[n]->[r]
with f(i) != f(j) on every edge. It need not be surjective. Define

    asc_G(f) = # {edges {i,j}: i<j and f(i)<f(j)}.

For a permutation word sigma=(sigma_1,...,sigma_n), put

    D_G^0 = {sigma: sigma_i>sigma_(i+1) implies {sigma_i,sigma_(i+1)} is an edge},
    ginv_G(sigma) = # {(i,j): i<j, sigma_i>sigma_j,
                                      {sigma_i,sigma_j} is an edge}.

A partition of n is a finite nonincreasing tuple of positive integers summing
to n. Its length can be zero only for n=0. Write

    e_k(x_1,...,x_r) = sum_(S subset [r], |S|=k) prod_(c in S) x_c,
    e_lambda = prod_(k in lambda) e_k,     e_empty = 1.

All identities below are identities of polynomials with exact integer
coefficients; q is an indeterminate, not a numerical sample.

## 2. Computer-assisted finite theorem

For every n in {0,...,6} and every h in H_n, the table in the uniquely indexed
certificate file defines a function theta_hat_G:D_G^0 -> Partitions(n), and

    chi_G(x_1,...,x_n;q)
      = sum_(sigma in D_G^0) q^ginv_G(sigma) e_(theta_hat_G(sigma))(x_1,...,x_n),

where chi is the proper-colouring sum with ascent exponent defined above.
Equivalently, for every alpha in N^n and d in N, both sides have equal
[x^alpha q^d] coefficients. The e-coefficients are nonnegative integers at
every q degree. All 197 graph instances were accepted by the standalone checker.

The evidence is a completely finite exhaustive computation with explicit
certificates and a separate, replayable checker. It is not a Lean/kernel theorem.
Sections 3 through 8 justify that the checked predicates match this statement.
The actual outputs, including counts and all positive acceptance events, are in
logs/verify_0_6.log. The verification program itself is part of the deliverable,
not an unspecified external solver.

## 3. Exhaustiveness of the graph and permutation universes

The generator chooses h_i from max(i,h_(i-1)),...,n, using 1 as the previous
lower bound before the first coordinate. Every generated sequence satisfies
exactly the stated inequalities. Conversely, any sequence satisfying them follows
one and only one branch of this recursive enumeration. This includes the empty
sequence as the one terminal branch when n=0.

The verifier constructs its universe differently: it enumerates all length-n
combinations with replacement from 1,...,n, then keeps those satisfying h_i>=i.
Combinations with replacement enumerate each weakly increasing tuple once. The
filter supplies exactly the remaining condition. It compares every catalogue
record, including its natural labels and position in the ordered list, against
this independent universe and rejects extra, missing or duplicated certificates.
Both enumerations give counts 1,1,2,5,14,42,132, respectively. These observed
counts are not an assumption in either enumeration.

No graph-isomorphism reduction occurs. For example h=(1,3,3) and h=(2,2,3) are
both retained: they place the single edge on different natural labels. More
generally, h_i is recovered from a labelled graph as the greatest later neighbor
of i, or i itself when there is no later neighbor. Different valid h therefore
give different labelled inputs.

The generator uses itertools.permutations on the ordered list 1,...,n. The
verifier uses an independent lexicographic-successor algorithm, beginning with
the increasing word. Its successor is the least lexicographically larger word,
and it terminates exactly at the decreasing word. It checks that n! words have
been visited, in addition to applying the domain test. The empty word is visited
once. No permutation outside D_G^0 may appear in the witness; every member must
appear exactly once. Duplicate detection is performed before row aggregation.

The generator computes graph inversions by iterating over pairs of positions.
The verifier instead computes the inverse position of each letter and counts an
edge {a,b}, a<b, exactly when b appears before a. These descriptions count the
same inverted edges without reusing the generator's implementation.

## 4. Colouring coefficients and symmetry are checked, not imposed

The generator assigns one of n colours to each vertex in increasing vertex
order. It prunes a prefix only when that prefix already violates an edge
inequality. Such a prefix cannot extend to a proper colouring. Every proper
colouring determines one surviving branch and is counted once. When a vertex j
is added, each earlier edge {i,j} contributes an ascent exactly when the earlier
colour is smaller. The full length-n exponent vector alpha records how many
vertices receive each specific colour.

The verifier takes a different route. It visits all n^n colour functions as a
Cartesian product, tests all edges for properness only after a full tuple is
formed, then counts ascents and multiplicities directly. It checks the number of
candidate functions. For n=0 this product contains one empty function, so 0^0=1
is an enumeration convention consistent with the unique empty function.

Neither algorithm replaces colours by canonical representatives during
colouring enumeration. Each (full alpha,d) count is retained and exported.
The sparse table omits zero entries. Degree n homogeneity makes every coefficient
with sum(alpha)!=n zero on both sides; degrees beyond the number M of edges also
vanish. Thus the sparse representation, together with explicit support bounds,
represents every coefficient, not just those selected for basis conversion.

The generator checks every weak composition alpha of n into n entries, at each
d=0,...,M, against the coefficient at its decreasing rearrangement. In particular,
missing zero coefficients are included. This establishes symmetry before using
partition representatives in the basis calculation.

The verifier checks invariance under every adjacent transposition of the colour
coordinates at every nonzero entry. Adjacent transpositions generate the full
symmetric group. If a zero entry were exchanged with a nonzero entry, testing the
nonzero entry in the reverse direction would detect the failure, so omitting an
all-zero-to-zero comparison is harmless. Thus this independent symmetry check
also covers every coefficient. It additionally verifies the colour reversal
relation between (alpha,d) and (reverse(alpha),M-d).

## 5. Exact elementary basis calculation

Let P_n be all partitions of n, sorted lexicographically as nonincreasing tuples.
For mu in P_n, let a(mu) be the tuple mu padded with zeros to length n. Define

    A_(mu,lambda) = [x^a(mu)] e_lambda(x_1,...,x_n).

This is the coefficient of ONE representative monomial. It is not the sum over
its orbit. Since e_lambda is symmetric, A is also the transition matrix from
e-products to the monomial symmetric basis m_mu, whose convention is one copy of
each distinct monomial. This normalization matters when parts repeat or zeros
are present.

For the generator, A is computed by multiplying the literal subset sums defining
e_k, with integer sparse polynomial convolution. Starting from 1, each factor
chooses a k-element colour subset and increases its coordinates by one. Repeated
factors remain separate factors and all multiplicities are retained.

Symmetric homogeneous degree-n polynomials have one freely chosen coefficient
for each exponent orbit, hence are identified with vectors indexed by P_n.
Each e_lambda is symmetric and homogeneous. For n=0,...,6, the exported square
matrices have dimensions 1,1,2,3,5,7,11 and determinants 1,1,-1,-1,1,-1,-1.
The independently checked matrices and inverses therefore establish that these
e-products form an integral basis in precisely these finite degrees. This
finite matrix argument suffices; no positivity theorem is being used.

At degree d, let b_d(mu)=[x^a(mu) q^d]chi_G. The generator solves

    A c_d = b_d

by Fraction-based Gauss-Jordan elimination. It checks each pivot, the identity
reduction, the matrix/inverse product, integrality of the determinant and all
inverse entries, integrality of every c_d(lambda), and c_d(lambda)>=0. It then
reconstructs every full colouring coefficient from these e-coefficients, rather
than checking only representative entries.

The verifier's optional basis audit rebuilds every A entry by enumerating 0/1
matrices as described below, independently checks the exported inverse product,
and uses fraction-free Bareiss elimination for the determinant. This differs
from the generator's rational elimination. The basis audit is supplementary:
verify_graph neither reads this matrix data nor performs a basis conversion.

## 6. Coefficient-count identity and the synthesized map

For each d, let P_d be the permitted permutations with graph-inversion degree d,
sorted lexicographically. The generator verifies the necessary equality

    |P_d| = sum_(lambda partitions n) c_d(lambda)

for every d=0,...,M, including degrees with no entries. When it holds and all
c_d(lambda) are nonnegative integers, form a slot list by repeating each lambda
c_d(lambda) times, in increasing lexicographic partition order. Assign the jth
permutation in P_d to the jth slot. No choice remains once these orders are fixed.
The output theta_hat_G is the union of these maps over all degrees.

For each lambda and d, exactly c_d(lambda) permutations receive this slot.
Consequently the weighted e-product sum over permutations equals the verified
e-basis expansion. This is sufficient to produce a finite witness, not merely
a necessary degree-count test. The separate verifier checks sufficiency directly
at the level of every raw monomial coefficient.

This allocation deliberately uses the computed e-coefficient list. The paper's
algorithm expressly does not take that list as input. No identification of the
individual assignments with the paper's Lambda/theta construction or Lean's
selectedTable is asserted. Many finite tables can satisfy the same identity.

## 7. Why the standalone verifier proves the coefficient identity

For each witness row, the verifier first validates the actual permutation,
its membership in D_G^0, its exact graph-inversion degree, and a partition of n.
After proving the rows constitute the whole domain once each, it groups rows by
(partition,d). The redundant elementary summary must equal these row counts,
which are nonnegative integers. The degree totals are checked independently.

For a partition lambda=(lambda_1,...,lambda_l), an individual monomial term of
e_lambda is specified by an ordered tuple (S_1,...,S_l) of colour subsets with
|S_j|=lambda_j. Represent S_j by an n-bit mask. Its total exponent vector has
alpha_c equal to the number of rows whose masks contain c. Conversely every such
mask tuple chooses exactly one term in the product definition. Thus enumerating
all these tuples and recording their column sums computes exactly every
coefficient of e_lambda. Repeated equal parts still have distinct row positions,
so there is no division by factorials and no lost multiplicity.

The verifier performs this direct mask enumeration using product(*choices).
It does not use the generator's convolution, matrix inverse, e-coefficients, or
positivity theorem. Multiplication by the number of witness rows in each bin
then yields the full coefficient dictionary of the right-hand side. The
independently re-enumerated colouring dictionary is the left-hand side. The
checker compares the dictionaries exactly, with diagnostic first differences,
and rejects if any coefficient differs or if either side has an extra entry.
This is precisely the theorem in Section 2.

Hashes bind the delivered bytes to their catalogue and package manifest, but
hash agreement alone is not mathematical evidence. The semantic checker recomputes
the contents even after the hashes match. Mutation tests bypass only outer
catalogue hashes where necessary to exercise those semantic checks directly.

## 8. Boundary cases and the paper's path

For n=0 there is one graph, one empty colouring, one empty permutation, one empty
partition, and both sides are 1. For n=1, h=(1), both sides are e_1. The test for
the edgeless graph on two vertices checks four proper colourings in two available
colours, thereby detecting an accidental restriction to surjective colourings.

For h=(2,3,3), the graph is the naturally labelled path 1--2--3. Its polynomial is

    chi = q e_(2,1) + (1+q+q^2) e_(3).

The coefficient of x_1*x_2*x_3 is 1+4q+q^2. Each of the six monomials whose
exponent vector is a rearrangement of (2,1,0) has coefficient q. Our table is

    123 -> degree 0, partition (3)
    132 -> degree 1, partition (2,1)
    213 -> degree 1, partition (3)
    321 -> degree 2, partition (3).

This specific choice follows our lexicographic allocation, not a computation of
the paper's map. Swapping the partitions of 132 and 213 produces another valid
witness; the positive regression verifies that the checker accepts it.

## 9. Extension to other finite alphabets for the SAME fixed graphs

This is a mathematical consequence, not an additional exhaustive computation.
A monomial of total degree n uses k<=n distinct colours. Write them in increasing
order c_1<...<c_k and replace them by 1,...,k. This is a bijection on the colourings
contributing to that monomial and its packed counterpart. It preserves equality
and all strict colour comparisons, hence properness and the ascent exponent.
The packed counterpart is present among the n-colour coefficients already checked.

For e_lambda, the identical relabeling gives a bijection of the ordered subset
choices contributing to those two monomials. Subsets cannot use a colour whose
exponent is zero. The coefficient of the corresponding right-hand side is thus
also unchanged. Equality of the packed coefficients in n colours proves equality
of the original coefficients in any r colours. All polynomials are homogeneous
of degree n, so there are no further coefficients to check. For r=0 and n>0 both
sides vanish; for n=0 both equal 1 for every r.

It follows that each delivered theta_hat_G gives the formal symmetric-function
identity for its fixed enumerated graph. This argument uses neither the general
positivity theorem nor an already existing permutation witness. It does not
extend the range of graphs beyond n=6 and is not a new general positivity proof.

## 10. Dependencies and limitations

Mathematical dependencies used here are elementary finite enumeration, integer
polynomial arithmetic, permutation order and inversions, the subset definition
of elementary functions, rational linear algebra, and the arguments above.
The graph and permutation definitions are inherited from the pinned sources.
The proof does not depend on the manuscript's packet switch, wall positivity,
triangular embedding, exact-mask cancellation, or the general Lean historyWitness.

Computational dependencies are the included Python programs, CPython and its
standard library, and the operating-system/runtime execution. No third-party
solver or numerical tolerance is used. The separate code paths reduce correlated
implementation risk, but their author was the same assistant in the same session.
There has been no independent external review and no kernel formalization of the
checker or of its correspondence with the source definition. These qualifications
are part of the result, not hidden assumptions.
