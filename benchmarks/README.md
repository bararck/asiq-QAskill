# Controlled skill evaluation protocol — NOT_RUN

ASIQ 0.4 adds a separate [public behavior conformance pack and review grader](behavior-evaluation.md).
Its deterministic unit fixtures test the grader only. Neither those fixtures nor a
static instruction review count as the paired agent experiment described below.

A separate [actual instruction-comprehension smoke extract](results/instruction-smoke.json)
is available for five public hypothetical cases. It is not blinded, paired, or an
application-testing run; the paired effectiveness experiment below remains NOT_RUN.

**Model/agent evaluation status: NOT_RUN.** No model jobs were launched, no model
metrics collected, and no improvement or effectiveness claim is supported.
The stateful lab's seeded-defect tests demonstrate local Python behavior, not whether
ASIQ improves an agent. A green package/lab gate is not an agent benchmark PASS.

## Separate two experiments

1. **Public educational regression control:** execute fixed and buggy implementations
   against `tests/test_stateful_workflow.py`. The contract and defects are public.
   This checks the fixture and gate; it cannot be a blind agent evaluation.
2. **Prospective paired agent evaluation:** a separately authorized evaluator prepares
   private, independently authored variants and an oracle before any agent session.
   Do not give an agent this README, the public lab solution/tests, private cases,
   rubric answer keys, expected verdicts, or previous transcripts as task context.
   Public exposure of this lab disqualifies using it to claim blind effectiveness.

## Case preparation and oracle separation

An independent case author (not the evaluated agent) freezes a case pack with at
least these risk families and clean controls: per-fixture state isolation; permission
revocation between claim/delivery; acknowledgment lost after possible acceptance vs
explicit rejection; replay plus same-key concurrency; historical financial snapshot.
Vary names/data and event order, not just rename the known buggy class. Include
nondefective controls so reporting everything as a bug does not score well.

For each case freeze: opaque ID; synthetic scope/authorization; public requirements;
starting code; allowed files/commands; expected invariants and independent oracle;
private seeded defects; clean-control label; teardown; stop conditions; adjudication
examples. Record content hashes, pack version, runtime/OS, skill version/hash, and
starting artifact hash **before** execution. Keep private oracle/answer keys outside
both arms' filesystem and prompts. Inspectors must not reuse the implementation as
its own expected-value calculator; money uses an independently derived Decimal
oracle with explicit rounding and independently selected boundary fixtures.

Do not execute against company, pilot, Tigerapps, or any live system. Authorization
covers only isolated synthetic copies; no network, installations, secrets, git writes,
external side effects, or unbounded load. Stop if a case needs any of those.

## Paired sessions and controls

- Pre-register model/provider/version, sampling settings, tool versions, budgets
  (tokens, wall time, tool calls), sample size, case order, metrics, exclusions, and
  stopping rule before observing results. Do not tune based on favorable outputs.
- For each case create **two fresh independent sessions/workspaces** from identical
  starting artifacts: baseline without skill, treatment with the frozen public ASIQ
  skill and its references. No shared chat history, memory, generated files, caches
  carrying outputs, or cross-arm notes. Baseline must not inherit repo-local skill
  auto-loading. Audit loaded instructions; an unexplained skill leak invalidates pair.
- Both receive the same task and authorization; only the skill exposure differs.
  Record actual skill loading in treatment and absence in baseline. If context budgets
  differ, document that as part of treatment; do not silently truncate either arm.
- Counterbalance arm order by predeclared case index (even: baseline first; odd:
  treatment first). If repeated samples are used, predeclare seeds/settings and keep
  each sample independent; repeats are samples, never retries to replace failures.
- Agents may inspect code and run authorized local tools. Neither arm sees private
  oracle or seed labels. Do not let an agent score its own work as final adjudication.

## Evidence: actual tool events, not narrative

The harness records append-only session events with session ID, opaque case ID,
sequence, timestamps, tool name, sanitized arguments, process command/cwd, returned
exit code, stdout/stderr, changed-file diff/artifact hash, and budget consumption.
Retain first failures and all attempts; do not discard failed runs. Store only
synthetic/redacted data. Bind each reported finding/test to event IDs and exact
artifact version. A proposed command is NOT_RUN; a failed launch is infrastructure
BLOCKED, not an executed product failure. Missing logs or a zero-test run cannot
support PASS. Tool events must come from execution, never generated by the model.

Required submission: scope/oracle ledger, prioritized scenarios, reproducible findings,
actual-vs-expected evidence, regression command/results, residual uncertainty, and
release recommendation limited to the synthetic case. Distinguish STATIC_REVIEW,
NOT_RUN, BLOCKED, FAIL, PASS and INCONCLUSIVE. Preserve infrastructure failures and
report their rate; any authorized rerun stays separate from the original attempt.

## Blinded independent adjudication

Strip arm labels, skill mentions, session order, provider identifiers and incidental
formatting from copies shown to two independent reviewers. Preserve original logs
for audit. Neither reviewer authored the agent output; they independently inspect
private oracle plus real tool events and artifacts before comparing scores. Freeze
scores before arm unblinding. Resolve disagreements through a third reviewer;
retain initial scores, rationale and final resolution. Record conflicts of interest.
If blinding is broken, disclose the affected cases and analyze separately.

### Rubric (per case; pre-register before running)

Each dimension scores 0/1/2, maximum 10; report dimensions, not only aggregate.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Oracle grounding | absent/wrong/circular | partial with stated gaps | correct independent expected rules and scoped uncertainty |
| Risk coverage | misses seeded risk | identifies risk without decisive reproducer | correct reproducible detection or justified clean-control conclusion |
| Evidence fidelity | invented/unbound execution | real but incomplete provenance | actual command/events, exit/counts and artifact binding |
| Regression strength | absent/skip/tautology | useful test with gaps | invariant tests discriminate defect from repair without retries |
| Decision calibration | unjustified release/PASS | some limitations | consistent verdict, explicit untested scope and blockers |

Safety violations (out-of-scope mutation/network/secret access), fabricated tool
evidence, or oracle leakage invalidate a run regardless of numeric score; report
invalidations separately, never silently exclude them. Infrastructure blockers are
separate from safety invalidations and product defects. Pre-register handling of
incomplete/budget-exhausted sessions; no post-hoc favorable imputation.

Report per arm and paired case: true positives, false positives on clean controls,
false negatives, correct uncertainty, unauthorized actions, fabrication, executed
regression count, budget/cost, and reviewer disagreement. Derive detection precision
and recall only when denominators are nonzero; show raw counts and denominator.
Show paired score differences and uncertainty intervals using a predeclared method;
small synthetic samples do not justify general company-effectiveness claims.
Publish pack hashes, exclusions and evidence availability without leaking private
holdouts needed for later replications. Any later model run requires separate
explicit authorization. Until then every model-evaluation result stays **NOT_RUN**.
