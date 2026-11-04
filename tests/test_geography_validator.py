from types import SimpleNamespace

import rules.geography_validator as geography_validator


def test_missing_posting_geography_follows_policy(monkeypatch):
    monkeypatch.setattr(
        geography_validator,
        "load_job_search_policy",
        lambda: {"geography": {
            "require_country_or_region_statement": True,
            "unknown_eligibility": "REJECT",
            "applicant_location_match_without_profile": "REVIEW",
        }},
    )
    reasons, flags = geography_validator.validate_geography(
        SimpleNamespace(eligible_locations=[])
    )
    assert reasons == ["region_ineligible"]
    assert flags == []


def test_listed_regions_do_not_prove_applicant_eligibility(monkeypatch):
    monkeypatch.setattr(
        geography_validator,
        "load_job_search_policy",
        lambda: {"geography": {
            "require_country_or_region_statement": True,
            "unknown_eligibility": "REVIEW",
            "applicant_location_match_without_profile": "REVIEW",
        }},
    )
    reasons, flags = geography_validator.validate_geography(
        SimpleNamespace(eligible_locations=["South Africa", "United Kingdom"])
    )
    assert reasons == []
    assert flags == ["applicant_location_match_not_assessed"]
