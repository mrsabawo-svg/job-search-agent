# Job Search Agent

Policy-governed discovery and qualification of legitimate, paid remote software-engineering opportunities.

## V1 policy
The canonical eligibility policy is [policy/job_search_policy.yaml](policy/job_search_policy.yaml). It governs role scope, employment type, remote-work requirements, compensation, geography, employer verification requirements, source governance, decision catalogues and execution stop limits. The policy remains in **draft** status until Milestone 1 acceptance evidence is complete.

Supporting policy data remains separate where it has a distinct responsibility:
- `policy/rejection_reasons.yaml` — reason-code and review-flag catalogue.
- `sources/approved_sources.yaml` — approved source registry.
- `sources/watchlist.yaml` — blocked/review source domains.

There is no second eligibility policy file. Changes to eligibility requirements belong in the canonical policy.

## Scope
- Remote backend, frontend, full-stack, software, platform, cloud, DevOps/SRE, data, ML and QA automation roles.
- Full-time and contract only.
- Explicit salary/hourly pay with amount, currency and period required.
- Employer ATS sources enabled by default; third-party boards require approval.
- Unknown facts become REVIEW, never an assumed pass.
- One policy-scope validator owns category, employment, remote-work and compensation eligibility; source, employer, geography and risk validators own their separate evidence domains.

## Architecture
- [Candidate Competency and Engineering Fit Architecture](docs/architecture/candidate_competency_model.md) — balanced assessment across technical capability, engineering practice and professional engineering behaviours, grounded in evidence.
- Candidate suitability is a separate subsystem from opportunity qualification.
- The competency architecture does not change or interrupt the active Milestone 1 repair sequence.

## Safety
This milestone qualifies opportunities only. No application submission, legal declarations, or applicant-data disclosure. Human review and explicit approval are mandatory before any future submission feature. Run budgets are defined in the canonical policy and must be checked through `workflow.stop_conditions.enforce_run_limits` before any future execution-side effect.

## Setup
Python 3.11+: `pip install -r requirements.txt` then `pytest -q`.
