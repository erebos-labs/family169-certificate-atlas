# Data format and independent acceptance

All JSON is UTF-8. Dataset files use deterministic compact JSON with sorted keys
and a final newline. Graph labels and h values are 1-based. Exponent-vector
coordinate 0 denotes x_1. A partition is stored in nonincreasing positive parts;
the empty partition is []. q coefficient arrays are in ascending degree order.

## Catalogue

atlas/atlas.json contains schema family169-atlas-v1, version 1.0.0, the pinned
source_commit, min_n=0, max_n=6, and the complete ordered graph list. Each record
stores n, h, relative certificate path and SHA-256 of those file bytes. The order
is increasing n, then lexicographic h. The verifier computes that universe anew;
it does not trust the catalogue's assertion of completeness.

## Graph certificate

schema: family169-certificate-v1
source_commit: fixed upstream pin
n: graph size
h: full weakly increasing extensive sequence
edges: all ordered endpoint pairs [i,j] with i<j, representing unordered edges
monomials: [{alpha: full length-n exponent vector, degree: d, coefficient: count}]
elementary: [{partition: lambda, q_coefficients: [c_0,...,c_M]}]
witness: [{permutation: full word, degree: d, partition: lambda}]

There is one monomials entry for each NONZERO coefficient. Entries are ordered
by full alpha and then degree, without merging distinct colour vectors. All
unlisted entries are zero. Homogeneity and the degree bound establish that
entries outside sum(alpha)=n and 0<=d<=M are zero on both sides. elementary omits
shapes whose entire q polynomial is zero, but retains zeros inside every
included degree array. The witness lists permitted permutations once each in
lexicographic order. The verifier validates the identity even for a differently
ordered or differently allocated valid table; deterministic allocation is a
generator property, not a uniqueness assertion about witnesses.

## Basis data

basis/nNN.json records n, all lexicographically sorted partitions,
zero-padded representative exponent vectors, matrix_rows_mu_columns_lambda,
inverse_rows_lambda_columns_mu, and determinant. The matrix entry is the
coefficient at ONE representative exponent vector, never the total over a
monomial orbit. These seven files document the exact basis calculation.
They are not used by verify_graph, and --skip-basis never reads them.

## Strictness and trust boundaries

Duplicate JSON keys and duplicate monomial/permutation/shape entries are rejected.
Integer fields exclude booleans where used mathematically. The complete h universe,
certificate binding, permitted-domain coverage, source degrees and full polynomial
coefficients are rechecked. Wrong inputs produce a VerificationError with a code
and, where useful, the first coefficient difference. No assertion can silently
turn these checks off under Python -O. Hash verification is separate from semantic
verification. The documented scripts are for bounded local research data, not a
hardened parser service for arbitrary hostile multi-gigabyte files.
