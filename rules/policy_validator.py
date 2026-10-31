from policy_loader import load_job_search_policy
from schema.job_record import JobRecord


def validate_policy_scope(job: JobRecord) -> list[str]:
    policy = load_job_search_policy()
    reasons = []

    if job.category.value not in policy["target_categories"]:
        reasons.append("off_domain")
    if job.employment_type not in policy["employment_types"]:
        reasons.append("employment_type_not_allowed")
    if policy["workplace"] == "remote_only" and job.workplace != "remote":
        reasons.append("not_remote")

    accepted_pay_types = set(policy["compensation"]["accepted_types"])
    if job.compensation.type.value not in accepted_pay_types:
        reasons.append("pay_unstated")

    return reasons
