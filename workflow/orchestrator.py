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

    reasons += validate_source(job.source, str(job.source_url))
    reasons += validate_pay(job.compensation)
    reasons += validate_remote(job.workplace)
    reasons += validate_employer(job.employer_name, job.employer_domain)
    reasons += detect_risk(job.description_text)

    reasons = list(dict.fromkeys(reasons))
    decision = DecisionState.REJECT if reasons else DecisionState.REVIEW

    return ValidationResult(
        job_id=job.job_id,
        decision=decision,
        reason_codes=reasons,
        review_flags=review_flags,
        policy_version=policy_version,
    )
