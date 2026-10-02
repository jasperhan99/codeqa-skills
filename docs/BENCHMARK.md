# Earlier diagnostic benchmark

On 2026-10-02, a bounded Python dependency scheduler task was run with
`openai-codex/gpt-6-luna` for development and `gpt-6-astra` for independent QA,
with medium thinking. Human approval waiting and release were excluded.

| Variant | Run 1 | Run 2 | Mean |
| --- | ---: | ---: | ---: |
| Original v3.2 workflow | 238 s | 250 s | 244 s |
| Continuous-coordinator optimized workflow | 222 s | 225 s | 223 s |

All four samples passed 13 frozen acceptance methods and first-round independent
QA. The observed mean difference was about 8.4%, mostly in finish/record keeping;
it is not a statistically established speedup or a causal attribution to one rule.
No post-review repair was needed, so reproduction-before-repair savings were not
measured. The original workflow also retained its coordinator context in this test.

A separate direct-development sample finished in 96 s, or 130 s including a
supplemental QA call. Another direct sample entered repetitive generation and was
manually terminated at 260 s. It was retained as a failed sample, not replaced or
included as a successful completion time.

The test predates the skill packaging in this repository. It does not benchmark
skill loading, local migration, or guarantee future results. Detailed local logs
remain under `benchmark-results/`, which is excluded from Git because it includes
large transcripts, generated repositories and machine-specific data.
