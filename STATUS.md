# Current status: release v1.0.1

All 197 naturally labelled graphs with 0<=n<=6 have verified synthesized finite
witnesses. The 205 dataset JSON files and six original mathematical/replay scripts
are unchanged from the v1.0.0 handoff.

The independent Atlas audit is complete. Normal Python verification includes
all seven basis matrices and inverses; an uninterrupted complete replay reproduces
all dataset files byte-for-byte. A third mathematical implementation confirms
the domain, partitions, degrees and full polynomial identities. All 792 supplied
negative controls also reject under Python -O. Additional CLI controls repair
catalogue hashes before testing mathematical corruption.

Current evidence is in independent/. Historical original reports are preserved
unchanged under historical/ and are superseded for execution/review status only.
Their original scope limitations still apply.

This is an authorized Erebos Labs public finite-data/software release. The user
approved publication after the independent audit. No general theorem, paper-map
reproduction, Lean selected-table reproduction, novelty or priority is claimed.
The full manuscript, Lean import closure and axioms remain outside this audit.
No Lean compilation or human referee review was performed.

The GitHub Actions workflow runs the bounded complete normal replay, third checker,
optimized controls and additional probes on Linux Python 3.11/3.13 and macOS
Python 3.14. Run results and publication delivery checks are reported separately.
