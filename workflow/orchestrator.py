from schema.job_record import JobRecord
from schema.validation_result import ValidationResult
from domain.decision_states import DecisionState
from rules.pay_validator import validate_pay
from rules.remote_validator import validate_remote
from rules.employer_validator import validate_employer
from rules.risk_validator import detect_risk
def qualify_job(job:JobRecord,*,policy_version:int=1)->ValidationResult:
    reasons=[]
    reasons += validate_pay(job.compensation)+validate_remote(job.workplace)+validate_employer(job.employer_name,job.employer_domain)+detect_risk(job.description_text)
    reasons=list(dict.fromkeys(reasons))
    # Conservative: no candidate is ACCEPTED until source, location, role and evidence checks exist.
    decision=DecisionState.REJECT if reasons else DecisionState.REVIEW
    return ValidationResult(job_id=job.job_id,decision=decision,reason_codes=reasons,policy_version=policy_version)
