# Job Search Agent

Policy-governed discovery and qualification of legitimate, paid remote software-engineering opportunities.

## V1
- Remote backend, frontend, full-stack, software, platform, cloud, DevOps/SRE, data, ML and QA automation roles.
- Full-time and contract only.
- Explicit salary/hourly pay with amount, currency and period required.
- Employer ATS sources enabled by default; third-party boards require approval.
- Unknown facts become REVIEW, never an assumed pass.

## Architecture
- [Candidate Competency and Engineering Fit Architecture](docs/architecture/candidate_competency_model.md) — balanced assessment across technical capability, engineering practice and professional engineering behaviours, grounded in evidence.
- Candidate suitability is a separate subsystem from opportunity qualification.
- The competency architecture does not change or interrupt the active Milestone 1 repair sequence.

## Safety
This milestone qualifies opportunities only. No application submission, legal declarations, or applicant-data disclosure. Human review and explicit approval are mandatory before any future submission feature.

## Setup
Python 3.11+: `pip install -r requirements.txt` then `pytest -q`.
