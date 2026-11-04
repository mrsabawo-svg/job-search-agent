# Milestone 1 — Policy-to-Code Traceability Audit

**Audit date:** 2026-11-04  
**Policy version:** 1  
**Canonical policy:** `policy/job_search_policy.yaml`  
**Status:** Audit performed; Milestone 1 remains gated.

## Executive result

The eligibility policy, runtime validators, decision catalogue and regression tests are now aligned for the currently implemented qualification path. No runtime path emits `ACCEPT`; qualification produces `REJECT` for policy hard failures and `REVIEW` otherwise.

The remaining acceptance blocker is execution-boundary integration of run budgets. The repository does not yet contain a discovery/run executor or browser/application side-effect entrypoint. The strict `enforce_run_limits` guard is implemented and tested, but there is not yet a production workflow boundary that invokes it. This must be wired when the workflow execution layer is introduced; do not treat the guard API alone as proof that every future operation is protected.

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
| Run budgets | `workflow/stop_conditions.py` | Limit boundary, malformed counter, strict policy schema and guard exception tests |

## M1-POL-05 — Validator consolidation

**Complete.**
- Removed unused `rules/pay_validator.py` and `rules/remote_validator.py`.
- `rules/policy_validator.py` is the single policy-scope validator for role category, employment type, remote status and compensation.
- Source, employer, geography and risk validators remain separate because they own distinct evidence domains.
- Regression coverage confirms the consolidated policy validator remains the orchestrator's path.

## M1-POL-06 — Stop-condition hardening

**Guard implementation complete; runtime integration pending.**
- Stop limits are loaded from the canonical policy with exact-key, type, finite-value and non-negative checks.
- V1 policy cannot enable application attempts; the maximum remains zero.
- Counters reject booleans, negative values and non-integers.
- Runtime timestamps must be timezone-aware.
- `enforce_run_limits` raises `StopConditionReached` before a caller proceeds when any budget is exhausted.
- There is currently no production run executor or browser/application side-effect boundary to call this guard. The workflow milestone must make guard invocation mandatory at each such boundary and test that no operation proceeds after a stop condition.

## M1-POL-07 — Full policy-to-code regression audit

**Audit complete; one integration gate remains.**
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

Do **not** change policy status from `draft` and do **not** begin Milestone 2 until:
1. The stop-condition guard is wired into the actual workflow execution boundaries when those are introduced.
2. Each boundary has a regression test proving an exhausted budget blocks the operation.
3. The final integrated commit passes CI.
4. The complete Milestone 1 acceptance checklist is reviewed against this audit.

The audit deliberately records the unimplemented runtime boundary rather than claiming a guard function alone protects future execution.
