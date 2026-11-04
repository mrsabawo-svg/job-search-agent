# Milestone 1 — Policy-to-Code Traceability Audit

**Audit date:** 2026-11-04  
**Policy version:** 1  
**Canonical policy:** `policy/job_search_policy.yaml`  
**Status:** Execution-boundary integration implemented; final CI and acceptance review pending.

## Executive result

The eligibility policy, runtime validators, decision catalogue and regression tests are now aligned for the currently implemented qualification path. No runtime path emits `ACCEPT`; qualification produces `REJECT` for policy hard failures and `REVIEW` otherwise.

Run budgets now have a concrete in-memory execution boundary in `workflow/run_executor.py`. Its `execute` method checks canonical stop limits before source, discovery, candidate and validation callbacks; it reserves attempts before invoking callbacks so failures consume budget. `RunExecutor.qualify_job` routes the existing deterministic qualifier through the validation gate. Browser and application execution are explicitly unavailable in Milestone 1, and application attempts remain prohibited. Counters are process-local; durable counters, restart recovery and distributed coordination are deferred to later milestones. Future discovery adapters must use this executor; no live source adapter exists yet.

## Responsibility traceability

| Policy responsibility | Runtime consumer | Verification |
|---|---|---|
| Role category scope | `rules/policy_validator.py` | Category taxonomy and out-of-scope policy tests |
| Employment type | `rules/policy_validator.py` | Policy enforcement tests |
| Remote-only requirement | `rules/policy_validator.py` | Hybrid/onsite rejection tests |
| Compensation type and completeness | `rules/policy_validator.py` | Required-field and policy-toggle tests |
| Posting geography evidence | `rules/geography_validator.py` | Missing-country and applicant-match review tests |
| Employer identity/domain syntax | `rules/employer_validator.py` | Domain syntax and policy-toggle tests |
| Employer identity relationship uncertainty | `workflow/orchestrator.py` | Review-only integration test |
| Approved sources and watchlist | `rules/source_validator.py` | Source allow/deny, host matching, watchlist and path safety tests |
| Hiring-risk patterns | `rules/risk_validator.py` | Risk-pattern tests and catalogue parity test |
| Decision authorization | `policy_loader.py` | Catalogue completeness and runtime-code authorization tests |
| Stop-limit policy | `workflow/stop_conditions.py` | Limit boundary, malformed counter, strict policy schema and guard exception tests |\n| Run execution gate | `workflow/run_executor.py` | Exhausted budgets block callbacks; failed attempts consume budget; qualification uses validation gate |

## M1-POL-05 — Validator consolidation

**Complete.**
- Removed unused `rules/pay_validator.py` and `rules/remote_validator.py`.
- `rules/policy_validator.py` is the single policy-scope validator for role category, employment type, remote status and compensation.
- Source, employer, geography and risk validators remain separate because they own distinct evidence domains.
- Regression coverage confirms the consolidated policy validator remains the orchestrator's path.

## M1-POL-06 — Stop-condition hardening

**Guard and current validation execution-boundary integration complete.**
- Stop limits are loaded from the canonical policy with exact-key, type, finite-value and non-negative checks.
- V1 policy cannot enable application attempts; the maximum remains zero.
- Counters reject booleans, negative values and non-integers.
- Runtime timestamps must be timezone-aware.
- `enforce_run_limits` raises `StopConditionReached` before a caller proceeds when any budget is exhausted.
- `workflow/run_executor.py` invokes the guard before source, discovery, candidate and validation callbacks, then reserves the attempt before callback execution. Failed callbacks still consume the reserved attempt.\n- `RunExecutor.qualify_job` routes the existing qualification path through the validation budget gate.\n- Browser execution is unavailable in Milestone 1; application execution is blocked unconditionally. No browser or application side-effect boundary is implemented here.\n- Counters are in-memory and run-scoped. Durable persistence and restart recovery remain later-milestone responsibilities. Future adapters must use `RunExecutor.execute`.

## M1-POL-07 — Full policy-to-code regression audit

**Audit and current execution-boundary integration complete; final CI and acceptance review pending.**
- Every active hard-rejection code is implemented and documented.
- Runtime rejection codes are checked against the policy hard-rejection list and catalogue.
- Runtime review flags are checked against the policy review list and catalogue.
- Policy hard rejections and implemented validator outputs are asserted for exact parity.
- The role policy is validated by the loader and consumed by the policy validator.
- Employer and geography uncertainty remain review outcomes under the current policy.
- Qualification does not emit `ACCEPT`; unknown evidence cannot become an implicit pass.
- Source governance is enforced before a posting can proceed through qualification.
- No application submission or browser execution exists in this milestone.

## Release gate

The engineering implementation and current qualification execution-boundary integration are complete. Final CI passed for commit `27c35553cbb05bab40c35e2950cf55c4debfae78`.

The policy remains `draft` intentionally. This audit does not grant policy approval on behalf of the policy owner. Before treating the policy as operationally approved, the policy owner must review and approve its eligibility boundaries and source registry. Milestone 2 should begin only after that policy sign-off.

The current boundary is process-local and covers source, discovery, candidate and validation callbacks routed through `RunExecutor`. No live discovery adapter, browser execution or application submission path exists in Milestone 1. Future adapters must use this gate. Durable counters, restart recovery and cross-process enforcement belong to the persistence/workflow milestones.
