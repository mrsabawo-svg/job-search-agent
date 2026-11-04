# Milestone 2 — PostgreSQL Persistence Design

**Status:** Proposed design; implementation not yet started
**Milestone:** 2 — Persistence integrity
**Predecessor:** Milestone 1 policy v1 approved on 2026-11-04
**Next milestone:** 3 — Temporal workflow integrity

## 1. Objective and non-goals

PostgreSQL becomes the durable source of truth for qualified job records, source observations, validation decisions, run execution, budgets, audit events and future human approvals. The design must preserve provenance, make retries safe, survive process restarts and support deterministic reconstruction of why a decision was made.

This milestone does not add Temporal, live discovery adapters, browser automation, application submission, Redis or a dashboard. Application attempts remain prohibited by approved policy (max_application_attempts = 0). Candidate suitability remains separate from opportunity qualification.

## 2. Persistence principles

1. Persist facts and decisions separately. A job posting, an observation of that posting, and a validation decision are different records.
2. Preserve history. Re-observation or re-validation must not silently overwrite earlier evidence or decisions.
3. Use database constraints for invariants that must survive concurrent processes.
4. Use transactions for every multi-record state transition.
5. Make externally retried operations idempotent through stable idempotency keys.
6. Store policy version and a policy-content digest with each validation decision.
7. Store timestamps as timezone-aware PostgreSQL timestamptz, normalized to UTC by the application.
8. Keep audit events append-only to ordinary application roles.
9. Minimize applicant data. Do not store credentials, identity documents, payment details, or sensitive personal attributes.
10. Keep all database writes behind repository/service interfaces; validators remain pure and database-independent.

## 3. Proposed relational model

### 3.1 jobs

One canonical job identity within the system.

- id UUID PRIMARY KEY
- canonical_key TEXT NOT NULL UNIQUE
- first_seen_at TIMESTAMPTZ NOT NULL
- last_seen_at TIMESTAMPTZ NOT NULL
- created_at, updated_at TIMESTAMPTZ NOT NULL

canonical_key is generated deterministically from the approved source identity, not from title/company text alone. A source-specific external posting ID is preferred. If no stable external ID exists, use a documented canonical URL normalization strategy and preserve the original URL in the observation. Do not merge jobs across different sources solely because titles or employers look similar.

### 3.2 job_observations

Immutable source observations / posting snapshots.

- id UUID PRIMARY KEY
- job_id UUID NOT NULL REFERENCES jobs(id)
- source_type TEXT NOT NULL
- source_id TEXT NOT NULL — registry identifier, e.g. greenhouse
- external_job_id TEXT NULL
- source_url TEXT NOT NULL
- observed_at TIMESTAMPTZ NOT NULL
- content_hash TEXT NOT NULL
- normalized_record JSONB NOT NULL
- raw_payload JSONB NULL — only if a source adapter has a lawful, bounded reason to retain it
- created_at TIMESTAMPTZ NOT NULL
- UNIQUE(job_id, content_hash)

Keep raw payload retention optional and bounded. Do not persist arbitrary page HTML by default. The normalized record must be sufficient to reproduce the validator input. A changed posting creates a new observation; it does not overwrite an earlier one.

### 3.3 search_runs

Durable run identity and lifecycle.

- id UUID PRIMARY KEY
- status TEXT NOT NULL CHECK against the defined run-state vocabulary
- policy_version INTEGER NOT NULL
- policy_digest TEXT NOT NULL
- started_at TIMESTAMPTZ NOT NULL
- finished_at TIMESTAMPTZ NULL
- stop_reason TEXT NULL
- created_at, updated_at TIMESTAMPTZ NOT NULL

A run records the exact approved policy version and digest used. A policy change during a run must not silently change that run's governing policy.

### 3.4 run_operations

Durable operation reservations and outcomes, replacing process-local-only counters as the authoritative budget ledger.

- id UUID PRIMARY KEY
- run_id UUID NOT NULL REFERENCES search_runs(id)
- operation_type TEXT NOT NULL CHECK in source, discovery, candidate, validation (no browser/application operations in this milestone)
- idempotency_key TEXT NOT NULL
- status TEXT NOT NULL CHECK in reserved, succeeded, failed
- reserved_at TIMESTAMPTZ NOT NULL
- completed_at TIMESTAMPTZ NULL
- error_code TEXT NULL
- UNIQUE(run_id, operation_type, idempotency_key)

Reserve an operation in a transaction before invoking its callback. A repeated request with the same idempotency key returns the existing operation and must not consume a second attempt or repeat a completed side effect. A genuinely new attempt requires a new key. Failed attempts remain counted. Concurrent reservations must serialize against run budget accounting so two workers cannot both pass the final available slot.

Budget counts are derived from durable operation rows, not trusted caller-supplied counters. Candidate counting is distinct canonical jobs per run; source/discovery/validation budgets count reserved operation rows of their respective types. Runtime duration is evaluated from the persisted run start time.

### 3.5 validation_decisions

Immutable result of qualifying one observed posting under one policy snapshot.

- id UUID PRIMARY KEY
- job_id UUID NOT NULL REFERENCES jobs(id)
- observation_id UUID NOT NULL REFERENCES job_observations(id)
- run_id UUID NOT NULL REFERENCES search_runs(id)
- decision TEXT NOT NULL CHECK in ACCEPT, REJECT, REVIEW
- policy_version INTEGER NOT NULL
- policy_digest TEXT NOT NULL
- reason_codes JSONB NOT NULL
- review_flags JSONB NOT NULL
- validated_at TIMESTAMPTZ NOT NULL
- created_at TIMESTAMPTZ NOT NULL

Decision consistency must be validated by application contracts and database constraints where expressible: REJECT requires one or more reason codes; ACCEPT cannot have rejection reasons or unresolved review flags. The current Milestone 1 audit states that qualification emits REJECT or REVIEW, not ACCEPT; persistence must preserve that fact and must not manufacture ACCEPT.

### 3.6 evidence_records

Structured evidence attached to an observation and/or decision.

- id UUID PRIMARY KEY
- observation_id UUID NOT NULL REFERENCES job_observations(id)
- validation_decision_id UUID NULL REFERENCES validation_decisions(id)
- field_name TEXT NOT NULL
- value TEXT NOT NULL
- source_url TEXT NOT NULL
- captured_at TIMESTAMPTZ NOT NULL
- provenance_type TEXT NOT NULL
- created_at TIMESTAMPTZ NOT NULL

Evidence is append-only. Do not treat a URL as proof that the employer or posting is independently verified. Avoid duplicating large descriptions into every evidence row; retain normalized snapshot content once and reference it.

### 3.7 run_events

Append-only audit trail for run lifecycle and material transitions.

- id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
- run_id UUID NOT NULL REFERENCES search_runs(id)
- event_type TEXT NOT NULL
- occurred_at TIMESTAMPTZ NOT NULL
- operation_id UUID NULL REFERENCES run_operations(id)
- job_id UUID NULL REFERENCES jobs(id)
- payload JSONB NOT NULL DEFAULT '{}'

Application roles may insert and read events but must not update/delete them. Event payloads must be bounded and must not contain secrets or unnecessary personal data.

### 3.8 human_approvals

A future-facing, inert record for explicit human decisions. It does not enable application submission in Milestone 2.

- id UUID PRIMARY KEY
- subject_type TEXT NOT NULL
- subject_id UUID NOT NULL
- action_scope TEXT NOT NULL
- decision TEXT NOT NULL CHECK in approved, rejected, revoked
- actor_reference TEXT NOT NULL
- decided_at TIMESTAMPTZ NOT NULL
- expires_at TIMESTAMPTZ NULL
- context JSONB NOT NULL DEFAULT '{}'

Approvals are scoped, time-bounded where appropriate, and immutable; revocation is a new record/event, not destructive editing. No approval row can override the v1 prohibition on application attempts.

## 4. Candidate profile persistence boundary

The accepted candidate competency architecture explicitly requires Milestone 2 to account for candidate profiles, competency evidence and assessment records. Reserve a separate bounded schema design:

- candidate_profiles: minimal applicant-controlled profile metadata and version; avoid unnecessary personal identifiers.
- candidate_competencies: versioned taxonomy references and candidate-declared competency claims.
- candidate_evidence: provenance, source reference, capture date, verification state, factual observation and limitations.
- candidate_assessments: versioned assessment output linked to profile version, taxonomy version, job and requirement set.
- candidate_assessment_items: requirement-to-competency mapping, evidence references and status (Demonstrated, Partial, Claimed, Unknown, Not met).

These records must remain logically and permissionally separate from job legitimacy decisions. Do not implement candidate-fit scoring or collect sensitive personal attributes as part of this milestone's core job qualification store. Exact fields and retention rules require a separate migration design before implementation.

## 5. Identity, deduplication and idempotency

- Primary keys are generated UUIDs, never source-provided IDs.
- Source identity is (source_id, external_job_id) when the source guarantees stability.
- If no stable external ID exists, canonical URL normalization is source-adapter-specific, deterministic and versioned.
- Preserve source URL exactly as observed, even when a normalized identity URL is used for deduplication.
- Do not deduplicate across different source registries without corroborating evidence and a reviewable merge record.
- Content hash is computed over canonical normalized data with stable key ordering and documented normalization.
- Idempotency keys are scoped to (run_id, operation_type) and are required for retryable operations.
- Unique constraints are the final concurrency guard; application pre-checks alone are insufficient.

## 6. Transaction boundaries

1. Create run: insert run and initial event atomically.
2. Reserve operation: lock or atomically update the run budget ledger, verify all applicable limits, insert reservation and event in one transaction. If a limit is reached, persist a blocked/stop event and do not invoke the callback.
3. Persist observation: upsert canonical job identity, insert immutable observation, link it to the run through an event; all in one transaction.
4. Persist validation: insert decision, evidence rows and corresponding event atomically. A partial decision must never be visible.
5. Complete operation: mark reservation succeeded/failed and append event atomically.
6. Finish run: set terminal state and finish timestamp and append event atomically.

Never hold a database transaction open while making a network request. Reserve first, perform the external read outside the transaction, then persist the result in a new transaction. This is safe because Milestone 2 has no live discovery adapter or browser side effects.

## 7. Migration and database policy

- Use versioned, checked-in SQL migrations with a migration ledger.
- Migrations are forward-only in production; destructive rollback is not an operational recovery strategy.
- Every migration must be repeatable only through the migration runner's ledger, not by silently ignoring arbitrary SQL errors.
- Add indexes for foreign keys, run/status/time queries, source identity, observation hashes and decision lookups.
- Use CHECK, NOT NULL, UNIQUE and foreign-key constraints for durable invariants.
- Use parameterized SQL exclusively.
- Application database credentials must not be superuser or schema-owner credentials.
- No secrets in repository, migration files, logs, fixtures or test output.

## 8. Test and CI acceptance requirements

Milestone 2 is not complete until integration tests run against a real PostgreSQL service in CI and verify:

- Fresh database migration succeeds; migration ledger records exact versions.
- Constraints reject invalid enum/state, missing references, duplicate identities and invalid decision combinations.
- Transaction rollback leaves no partial observation, decision, evidence or event set.
- Same idempotency key cannot double-consume an operation budget.
- Concurrent reservations cannot exceed a configured run budget.
- Failed reservations/operations remain counted as policy requires.
- Candidate count is distinct canonical jobs, not observation count.
- Repeated observations with unchanged normalized content are idempotent; changed content creates a new immutable observation.
- Policy version/digest is retained with each run and decision.
- Restart/reconnection reads the same run state and budget counts from PostgreSQL.
- Append-only event and evidence permissions are enforced.
- No Milestone 2 path enables browser or application execution.

## 9. Implementation sequence

M2-01 — Freeze this persistence contract and resolve design review findings.
M2-02 — Add PostgreSQL driver/configuration and migration tooling; no application logic yet.
M2-03 — Implement core schema and constraints for jobs, observations, runs, operations, decisions, evidence and events.
M2-04 — Implement repository interfaces and transaction-safe services.
M2-05 — Persist run budgets and make RunExecutor use the durable ledger without changing policy semantics.
M2-06 — Add candidate-profile/competency persistence tables as a separately scoped schema component, without integrating fit into qualification.
M2-07 — Add PostgreSQL integration and concurrency tests in CI.
M2-08 — Run traceability, migration and restart-recovery audit; close Milestone 2 only when all acceptance criteria pass.

## 10. Explicitly deferred

Temporal orchestration, live job-source adapters, browser automation, application submission, candidate-fit scoring, Redis, dashboard/UI and production deployment are outside this milestone. Milestone 2 must not silently pull any of them forward.
