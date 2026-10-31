from policy_loader import load_job_search_policy
from schema.job_record import JobRecord


def validate_policy_scope(job: JobRecord) -> list[str]:
    policy = load_job_search_policy()
    reasons = []

    category_value = getattr(job.category, "value", job.category)
    if category_value not in policy["target_categories"]:
        reasons.append("off_domain")
    if job.employment_type not in policy["employment_types"]:
        reasons.append("employment_type_not_allowed")
    if policy["workplace"] == "remote_only" and job.workplace != "remote":
        reasons.append("not_remote")

    accepted_pay_types = set(policy["compensation"]["accepted_types"])
    pay_type = getattr(job.compensation.type, "value", job.compensation.type)
    if pay_type not in accepted_pay_types:
        if pay_type == "commission":
            reasons.append("commission_only")
        elif pay_type == "equity":
            reasons.append("equity_only")
        else:
            reasons.append("pay_unstated")

    return reasons
