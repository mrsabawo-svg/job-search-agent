from policy_loader import load_job_search_policy
from schema.job_record import JobRecord


def validate_geography(job: JobRecord) -> tuple[list[str], list[str]]:
    """Separate posting eligibility evidence from applicant-location assessment."""
    policy = load_job_search_policy()["geography"]
    reasons: list[str] = []
    review_flags: list[str] = []

    if policy["require_country_or_region_statement"] and not job.eligible_locations:
        if policy["unknown_eligibility"] == "REJECT":
            reasons.append("region_ineligible")
        else:
            review_flags.append("geographic_eligibility_unclear")
    elif job.eligible_locations:
        # A posting's eligible regions do not establish that this applicant qualifies.
        if policy["applicant_location_match_without_profile"] == "REJECT":
            reasons.append("region_ineligible")
        else:
            review_flags.append("applicant_location_match_not_assessed")

    return reasons, review_flags
