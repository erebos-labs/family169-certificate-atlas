# Changelog

## v1.0.0, 2026-10-14

Initial private handoff, pinned throughout to
1581d4cbdd69a0faf34b2089614fe2a814316a6a.

Read all six requested sources, then the graph/reversal/completion definitions
and actual Lean Model. Audited current history, relevant source trees, indexed
code and issue/PR searches, and primary related computational documentation.
Recorded the pre-existing Lean finite Test and selectedTable rather than treating
the comparator's intentional sorry as an implementation defect.

Implemented exact generator and separately structured standalone verifier.
Completed n<=4 first (23 graphs; 96 negative mutations), froze its baseline,
then completed n=5 (42 additional graphs) and froze that baseline. The measured
gate permitted n=6. Completed all 197 graphs, 11,465 witness rows, seven basis
audits, six positive regressions and 792 negative mutations. Preserved 99
smaller-stage file hashes unchanged. No mathematical mismatch was encountered.

Added offline replay and checksum utilities, complete finite coverage/proof
notes, source and search audits, raw logs, resource metrics, licensing and
checksums. A clean dataset matched all 205 original JSON files byte-for-byte.
The final clean mutation run completed in a separate tool call after two outer
interactive-tool timeout interruptions. Kept both partial logs and did not label
either monolithic replay-driver attempt successful.

Retrieval limitations: direct container downloads encountered a DNS failure;
the required sources were nonetheless accessible and read through GitHub's
connector. The available connector rejected the Actions-artifact listing endpoint.
An initial issue search lacking its issue/PR qualifier was corrected. These
retrieval errors supplied no mathematical evidence and did not alter definitions.

No original input, upstream repository file, source pin, certificate baseline,
remote repository or external communication channel was modified. No Lean build,
independent referee review or publication occurred. There is no n>6 result.
