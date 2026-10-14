# Bounded prior-work and artifact audit

## Question and outcome

The question was whether an equivalent executable atlas already existed that
should be verified rather than duplicated. The bounded search did not locate
such an atlas. That is a statement about the inspected paths and search results,
not established novelty or an assertion that no equivalent work exists.

The immutable source is openai/math commit
1581d4cbdd69a0faf34b2089614fe2a814316a6a. At the time of the read on 2026-10-14,
the repository's most recent returned commit matched that pin. Path history for
lean/OAI/Combinatorics/Chromatic returned only initial commit
adc7f1241b42e322a6451854ab7e4b4c146bf78a. The relevant source trees, root history,
indexed Python-code search, and chromatic issue/PR searches were checked before
implementation. Exact request URLs and observed outcomes, including additional
closing checks performed after the core computation, are in search_observations.json.

## Existing material that overlaps with this task

The closest exact specification already exists in HistoryMainWitness.lean:
FiniteSearch.Test compares full colouring coefficients to permitted-word sums
of elementary subset-matrix coefficients. ElementaryAlphabetRigidity.lean
connects that test to polynomial equality, and Main.lean uses Encodable.choose
to select a successful table after proving existence. This is pre-existing
finite-test theory; the deliverable does not claim to invent it. The inspected
Witness directory contains eight Lean source files, not a packaged collection
of explicit small-graph certificate tables in that listing.

SageMath's official documentation supplies an earlier executable route to
chromatic quasisymmetric functions and symmetric-function basis conversion.
The Graph.chromatic_quasisymmetric_function documentation includes path and
complete-graph examples, conversion to symmetric functions, and examples where
a general graph's chromatic quasisymmetric function is not symmetric. These
are genuine computational antecedents, not an equivalent checked atlas of the
specific partition-valued permitted-permutation maps requested here. No Sage
implementation was imported or used as an oracle in this computation.

The paper's own discussion and its finite packet/wall rule are also antecedents.
Our map differs intentionally: it uses the computed final e-coefficient counts
to assign lexicographic slots. It therefore makes no progress on reproducing
the source's individual packet/wall choice, even when its final identity agrees.

## Search boundaries and inaccessible resources

The code search for chromatic Python in the repository returned zero indexed
results, with incomplete_results=false. Separate issue and PR searches for
chromatic returned zero. Closing checks for the phrase certificate atlas and
Hessenberg Python also returned zero. GitHub's releases listing was empty.
These observations do not imply that differently named code or external work
is absent. Search counts are not a mathematical or historical priority proof.

The Actions-artifacts listing endpoint was rejected by the available connector
as unsupported (HTTP 400 / INVALID_ARGUMENT). Therefore CI artifact contents
were NOT inspected and are not reported empty. Forks, unrelated branches,
private or unindexed repositories, all reasoning-trace archives, binary assets,
and every bibliography reference were not exhaustively audited. Source tree
metadata inspection is distinguished from reading every file in those trees.

Direct container downloading initially encountered a DNS failure. The requested
sources were still available through the GitHub connector, so their definitions
were read rather than reconstructed from memory. There is no missing essential
source for the finite specification. The paper's full proof dependency tree
was not part of this bounded implementation audit.

## Attribution and claim wording

The bounded result is an explicit, reproducible, separately checked finite
certificate handoff on the given definitions. It is not a new general positivity
proof, a correction to the comparator, an evaluation of selectedTable, or an
established novel finite range. No contributor was contacted and no remote
repository changes or publication were performed.
