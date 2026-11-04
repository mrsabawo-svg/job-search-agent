from policy_loader import load_job_search_policy
from schema.job_record import JobRecord


def validate_policy_scope(job: JobRecord) -> list[str]:
    policy = load_job_search_policy()
    reasons = []

    role_policy = policy["role"]
    category_value = getattr(job.category, "value", job.category)
    if role_policy["require_target_category_match"] and category_value not in policy["target_categories"]:
        if role_policy["unrelated_roles"] == "REJECT":
            reasons.append("off_domain")
    if job.employment_type not in policy["employment_types"]:
        reasons.append("employment_type_not_allowed")
    if policy["workplace"] == "remote_only" and job.workplace != "remote":
        reasons.append("not_remote")

    compensation_policy = policy["compensation"]
    accepted_pay_types = set(compensation_policy["accepted_types"])
    pay_type = getattr(job.compensation.type, "value", job.compensation.type)
    if pay_type == "unspecified":
        if compensation_policy["reject_unspecified"]:
            reasons.append("pay_unstated")
    elif pay_type not in accepted_pay_types:
        if pay_type == "commission":
            reasons.append("commission_only")
        elif pay_type == "equity":
            reasons.append("equity_only")
        else:
            reasons.append("pay_unstated")
    else:
        required_fields = {
            "amount": compensation_policy["require_amount"],
            "currency": compensation_policy["require_currency"],
            "period": compensation_policy["require_period"],
        }
        missing_fields = [
            field for field, required in required_fields.items()
            if required and getattr(job.compensation, field) is None
        ]
        if missing_fields:
            reasons.append("pay_unstated")

    return list(dict.fromkeys(reasons))
