# Stateful workflow regression lab

Independently written public-edition **synthetic educational code**, not a service,
company fixture, production implementation, integration test, or model benchmark.
Python 3.11/3.12 standard library only; no install, network, secrets, sleep, or random
inputs. Run from the public-edition repository root. Namespace packages are intentional.

## Synthetic contract / oracle v1

These rules are authoritative **only for this lab**; they are not inferred company
requirements. All keys and money below are synthetic.

| Requirement | Contract | Mandatory test suffix |
|---|---|---|
| ISO-1 | New workflow owns fresh job/provider/invoice state | fixture_isolation |
| AUTH-1 | A claimed job whose permission is revoked before delivery is REFUSED; provider is not called | permission_revoked_after_claim |
| ACK-1 | Provider accepts an effect then loses acknowledgment: UNKNOWN, never definitive REFUSED | ambiguous_provider_failure_is_unknown |
| ACK-2 | Provider explicitly refuses before effect: REFUSED | explicit_provider_refusal_is_refused |
| IDEM-1 | Reclaim/replay preserves DELIVERED, REFUSED, UNKNOWN; never resends, even after permission changes | replay_never_resends_terminal_or_unknown |
| IDEM-2 | Four simultaneous same-key workers produce one provider attempt/effect | concurrent_workers_send_once |
| STATE-1 | Unclaimed delivery raises KeyError with zero provider calls | unclaimed_delivery_has_no_effect |
| MONEY-1 | At issuance: round each price x quantity to cents HALF_UP, sum lines, round subtotal x tax to cents HALF_UP; retain historical total despite later tax changes | historical_snapshot_matches_independent_decimal_oracle |

Money domain: nonnegative finite decimal strings and positive integer quantities;
no currency conversion, refunds, discounts, statutory tax claims, or input-validation
coverage. The implementation uses exact Fraction arithmetic and integer cents; the
test oracle independently uses Decimal and explicit ROUND_HALF_UP. The fixture gives
43.15 at issuance, not 60.21 after changing the current rate.

`FixedWorkflow` serializes claim/delivery via an instance RLock and memoizes outcomes.
`BuggyWorkflow` deliberately shares job state, ignores current permission, resends on
replay/concurrency, calls ambiguous failure REFUSED, and recomputes historical tax.
The synthetic provider records attempts and accepted effects separately. Its timeout
is raised synchronously after acceptance, not a wall-clock timeout or real transport.
UNKNOWN requires reconciliation outside this lab; there is no automatic retry.

The barrier coordinates four real threads without relying on ordering or sleeps.
Its five-second timeout is a deadlock guard, not retry or timing-based acceptance.
Thread completion order is irrelevant. The fixed lock covers the in-memory provider
call; this is not a distributed exactly-once guarantee, durability mechanism, or proof
against process crashes. Revocation here is an explicit transition **between** claim
and delivery, not an independently racing authorization service.

## Regression gate

Portable command (Windows and Linux):

```
python -m unittest discover -s tests -p test_stateful_workflow.py -v
```

Default is fixed: **8 tests must run, zero skips/errors/failures, exit 0**. Missing lab
is an assertion failure, never a skip. No retries or expected-failure decorators.
Unknown `ASIQ_LAB_IMPLEMENTATION` values are hard errors. The parent repository owns
verifier/CI integration; discovery must include this mandatory test file.

For the negative control set `ASIQ_LAB_IMPLEMENTATION=buggy` in the process environment,
then run the same command. Bash example:

```
ASIQ_LAB_IMPLEMENTATION=buggy python -m unittest discover -s tests -p test_stateful_workflow.py -v
```

PowerShell equivalent: `$env:ASIQ_LAB_IMPLEMENTATION='buggy'`; run the portable command;
then `Remove-Item Env:ASIQ_LAB_IMPLEMENTATION`. Use separate processes for both controls.
Buggy must exit nonzero with assertion failures, not import/setup errors. A green buggy
run means the negative control is broken. This intentional failure is not a failed
package gate: the mandatory default uses the fixed implementation.

## Actual authoring evidence

Executed locally on Windows with Python 3.11.16; Linux and 3.12 were not executed here.
Every slice used the discovery command above before and after implementation:

- Isolation RED: 1 test, 1 assertion failure (mandatory lab absent), exit 1; GREEN: 1 OK.
- Revocation RED: 2 tests, missing deliver method error, exit 1; GREEN: 2 OK.
- Acknowledgment RED: 4 tests, 2 missing provider_outcome interface errors, exit 1;
  GREEN: 4 OK. These interface REDs establish absence, not behavioral defect detection.
- Replay/concurrency/state RED: 7 tests, 4 assertion failures (including subtests),
  exit 1; GREEN: 7 OK.
- Snapshot RED: 8 tests, missing issue_invoice method error; GREEN: 8 OK.
  The snapshot RED command also ran an independent calculator afterward, so its shell
  aggregate exit was 0 despite unittest reporting FAILED; it is not a passing test run.
- Completed buggy control: 8 tests, 8 assertion failures (subtests included), zero
  errors/skips, exit 1. Six test methods fail; explicit refusal and unclaimed delivery pass.
- Completed fixed control: 8 tests, zero failures/errors/skips, exit 0.

The completed negative control supplies behavioral evidence for all five seeded defect
families. These observations prove local code behavior only. Model evaluation is
**NOT_RUN**; see ../../benchmarks/README.md. There is no agent effectiveness PASS.
# Batas domain invoice

Lab fixed hanya menerima harga, kuantitas integer, dan tarif pajak nonnegatif.
Input negatif, kuantitas boolean atau pecahan ditolak sebelum invoice disimpan.
Kredit/refund bertanda berada di luar kontrak lab ini. Regression input-domain
menguji FixedWorkflow secara langsung, termasuk saat negative control dipilih.

