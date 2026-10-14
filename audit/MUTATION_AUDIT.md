# Actual negative and positive tests

The suite operates on a copy of a certificate in memory, leaving the originals
unchanged. For mathematical corruption tests it invokes verify_graph directly,
so the outer catalogue hash cannot be the reason for rejection. A test passes
only if the checker rejects with the intended VerificationError code. An
unexpected exception or unexpected rejection reason fails the suite.

For EACH of the 197 graphs, three mutations were applied: remove the first
permitted permutation, duplicate it, and change its recorded degree. They were
rejected by missing_permutation, duplicate_permutation, and either
wrong_graph_inversion_degree or degree_bound, respectively. There are 591 such
negative cases.

For each of the 195 graphs with n>=2, the first row's partition was changed to a
DIFFERENT VALID partition of n. The redundant elementary summary was recomputed
to agree with the altered rows. All 195 were rejected specifically by the final
full coefficient_identity comparison, not because of a stale summary, invalid
partition, or changed checksum. For n=0 and n=1 there is only one partition;
those two mutations are labelled inapplicable rather than falsely counted as
successful tests.

Six further negative cases changed, removed and duplicated a raw monomial entry
on the three-vertex path; introduced a duplicate JSON key; removed a catalogue
graph; and duplicated a catalogue graph. They were rejected by the intended
raw-coefficient, duplicate-entry, or catalogue-coverage checks. Thus the full
negative total is 591+195+6=792.

The n<=4 baseline independently completed the same suite on 23 graphs, giving
23*4-2+6=96 rejections. These are earlier-stage tests, not additional distinct
cases to add to 792.

Six positive regressions cover n=0, n=1, the edgeless and complete graphs on two
vertices, the paper's three-vertex path with its expected raw and e-coefficients,
and a different valid path witness. In the latter, the assigned partitions of
132 and 213 are exchanged. Since both permutations have degree 1 and the shape
counts do not change, the verifier must accept this alternative. It did. This
confirms the checker validates the identity, not the generator's private choice
of a valid assignment.

logs/tests_0_6.log contains every original
rejection and the final successful summary. logs/clean_replay/ contains the
independent regeneration's completed test log tests_0_6_completed.log and also
an explicitly incomplete earlier tests_0_6_interrupted.log. Only the completed final summary
is counted as a successful clean replay test.

Negative tests are regression evidence for the exercised error modes. They do
not prove the Python checker free of all bugs and are not a substitute for its
coverage argument or independent review.
