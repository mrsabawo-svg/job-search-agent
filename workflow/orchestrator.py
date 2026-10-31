from domain.decision_states import DecisionState
from rules.employer_validator import validate_employer
from rules.pay_validator import validate_pay
from rules.remote_validator import validate_remote
from rules.risk_validator import detect_risk
from rules.source_validator import validate_source
from schema.job_record import JobRecord
from schema.validation_result import ValidationResult


def qualify_job(job: JobRecord, *, policy_version: int = 1) -> ValidationResult:
    reasons = []
    review_flags = []

    source_findings = validate_source(job.source, str(job.source_url))
    review_flags += [code for code in source_findings if code == "source_requires_review"]
    reasons += [code for code in source_findings if code != "source_requires_review"]

    reasons += validate_pay(job.compensation)
    reasons += validate_remote(job.workplace)
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
        policy_version=policy_version,
    )
