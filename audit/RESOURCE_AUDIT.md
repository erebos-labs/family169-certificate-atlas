# Resource gate, actual runs and interruptions

The requested expansion rule was followed: all n<=4 certificates, verification
and mutation tests completed before n=5 was generated and benchmarked. Only
then was n=6 attempted. All original completed stages have metrics with return
code zero, timed_out=false, timestamps and the actual command. The computation
is bounded by n<=6 in the generator and verifier.

## Measured gate before n=6

The measured n=5 generation and verification stage wall times were
0.821438001 and 0.972671977 seconds, respectively. The largest measured child
RSS in those stages was 100,024,320 bytes. The projection used the exact ratio
of candidate-colouring workloads

    (132 * 6^6) / (42 * 5^5) = 46.922605714285716,

multiplied by three, plus 60 seconds of overhead. It gave 312.55294531727066
projected seconds for n=6. An eightfold RSS allowance gave 800,194,560 bytes.
These estimates fitted the remaining 7,200-second compute budget and the
2,000,000,000-byte memory budget. logs/budget_gate.json records the gate before
the n=6 stage. The estimates are resource planning, not a complexity theorem.

## Original completed computation

| Stage | Measured child-stage wall seconds | Peak child RSS bytes |
|---|---:|---:|
| generate_0_4 | 0.720940 | 99,209,216 |
| verify_0_4 | 0.722157 | 99,762,176 |
| tests_0_4 | 0.670627 | 99,762,176 |
| generate_5 | 0.821438 | 99,766,272 |
| verify_5 | 0.972672 | 100,024,320 |
| generate_6 | 4.329880 | 101,318,656 |
| verify_0_6 | 11.754597 | 102,494,208 |
| tests_0_6 | 15.562881 | 104,214,528 |

The sum of these measured stage wall times is
35.555192216 seconds. This is not the elapsed
time of the entire research conversation; source retrieval, review and writing
are excluded. Startup is included in stage timings. The largest recorded child
RSS is 104,214,528 bytes, approximately
99.387 MiB. RSS is measured for the child,
not the whole machine or all unrelated processes. Wrapper processes are not
included in that peak. All substantive children were run one at a time.

On Linux, run_stage.py applies RLIMIT_AS=2,000,000,000 bytes to each child and
subprocess timeouts. On macOS it deliberately does not set RLIMIT_AS, because
address-space reservations and platform behavior differ; it records native RSS
in bytes instead. The replay driver enforces an aggregate wall-time budget of
at most 7,200 seconds and applies the measured memory gate. This session did not
execute on Atlas or macOS.

## Replay and tool-level interruptions

The first all-in-one replay invocation requested a 60-second outer tool timeout.
The second requested 180 seconds. Both were externally interrupted during the
final mutation suite, after their graph generation and full verification had
already passed. No subprocess timeout metric was written for the interrupted
suite, so its exact termination time and cause beyond the reported outer timeout
are not inferred. These are NOT mathematical mismatches and NOT completed driver
runs. Both partial outputs are preserved: logs/interrupted_replay/ and the
interrupted_driver.log plus partial tests_0_6_interrupted.log in logs/clean_replay/.

The final mutation suite was rerun against the second clean dataset in a
separate tool call. It completed in 15.062900874 measured stage seconds and
rejected all 792 corrupted inputs. A separate byte-for-byte comparison then
verified all 205 JSON files against the original dataset. Thus a segmented clean
replay completed successfully. Its eight completed component stages used
35.755422747 measured seconds.
logs/clean_replay_summary.json expressly distinguishes this result from an
uninterrupted replay.py-driver run. There was no need to change generator,
verifier, certificates or mathematical definitions after either interruption.

These partial attempts and repeated successful tests remain well within the
requested two-hour computational scale; no n>6 computation was attempted. No
future-machine timing guarantee is made.

## Closing check without basis data and with assertions disabled

The separate command `python -O -u src/verify.py --atlas atlas --skip-basis`
also accepted all 197 graphs. It used 15.215008287 measured stage
seconds, with peak child RSS 112,005,120 bytes (106.816 MiB).
This is the largest RSS across all recorded completed runs, including this
supplementary check. It is distinct from the 99.4 MiB maximum in the original
eight stages. The log and metrics are preserved as verify_without_basis.*.
