from datetime import datetime, timezone

from domain.decision_states import DecisionState
from rules.employer_validator import validate_employer
from rules.policy_validator import validate_policy_scope
from rules.risk_validator import detect_risk
from rules.source_validator import validate_source
from schema.job_record import JobRecord
from schema.validation_result import Evidence, ValidationResult


def _build_evidence(job: JobRecord) -> list[Evidence]:
    captured_at = datetime.now(timezone.utc)
    observations = [
        ("job_id", job.job_id),
        ("title", job.title),
        ("employer_name", job.employer_name),
        ("source", job.source.value),
        ("source_url", str(job.source_url)),
        ("category", job.category.value),
        ("employment_type", job.employment_type),
        ("workplace", job.workplace),
        ("compensation.type", job.compensation.type.value),
    ]
    if job.employer_domain:
        observations.append(("employer_domain", job.employer_domain))
    if job.eligible_locations:
        observations.append(("eligible_locations", ", ".join(job.eligible_locations)))
    if job.compensation.amount is not None:
        observations.append(("compensation.amount", str(job.compensation.amount)))
    if job.compensation.currency:
        observations.append(("compensation.currency", job.compensation.currency))
    if job.compensation.period:
        observations.append(("compensation.period", job.compensation.period.value))
    if job.description_text.strip():
        observations.append(("description_text", job.description_text.strip()))

    return [
        Evidence(
            field=field,
            value=value,
            source_url=job.source_url,
            captured_at=captured_at,
        )
        for field, value in observations
    ]


def qualify_job(job: JobRecord, *, policy_version: int = 1) -> ValidationResult:
    reasons = []
    review_flags = []

    source_findings = validate_source(job.source, str(job.source_url))
    review_flags += [code for code in source_findings if code == "source_requires_review"]
    reasons += [code for code in source_findings if code != "source_requires_review"]

    reasons += validate_policy_scope(job)
    reasons += validate_employer(job.employer_name, job.employer_domain)
    reasons += detect_risk(job.description_text)

    if not job.eligible_locations:
        review_flags.append("geographic_eligibility_unclear")
    else:
        review_flags.append("applicant_location_match_not_assessed")

    reasons = list(dict.fromkeys(reasons))
    review_flags = list(dict.fromkeys(review_flags))
    decision = DecisionState.REJECT if reasons else DecisionState.REVIEW

    return ValidationResult(
        job_id=job.job_id,
        decision=decision,
        reason_codes=reasons,
        review_flags=review_flags,
        evidence=_build_evidence(job),
        policy_version=policy_version,
    )
