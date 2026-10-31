from pathlib import Path

import pytest

import policy_loader
from policy_loader import PolicyConfigurationError, _load_yaml, load_job_search_policy
from rules.risk_validator import PATTERNS


def test_yaml_loader_rejects_duplicate_keys(tmp_path, monkeypatch):
    (tmp_path / "duplicate.yaml").write_text(
        "review_flags:\n  duplicate: first\n  duplicate: second\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(policy_loader, "ROOT", tmp_path)

    with pytest.raises(PolicyConfigurationError, match="Unable to load policy file"):
        _load_yaml("duplicate.yaml")


def test_policy_rejection_catalogue_covers_all_validator_outputs():
    catalogue = _load_yaml("policy/rejection_reasons.yaml")
    documented = set(catalogue["rejection_reasons"])
    validator_outputs = (
        set(PATTERNS)
        | {
            "off_domain",
            "pay_unstated",
            "commission_only",
            "equity_only",
            "employment_type_not_allowed",
            "not_remote",
            "employer_unverifiable",
            "source_url_invalid",
            "source_blocked",
            "source_not_approved",
        }
    )
    assert validator_outputs <= documented


def test_policy_review_catalogue_covers_orchestrator_flags():
    policy = load_job_search_policy()
    catalogue = _load_yaml("policy/rejection_reasons.yaml")
    emitted_review_flags = {
        "source_requires_review",
        "geographic_eligibility_unclear",
        "applicant_location_match_not_assessed",
        "employer_identity_not_independently_verified",
    }
    assert emitted_review_flags <= set(catalogue["review_flags"])
    assert emitted_review_flags <= set(policy["human_review_required"])


def test_every_declared_hard_rejection_is_implemented_and_documented():
    policy = load_job_search_policy()
    catalogue = _load_yaml("policy/rejection_reasons.yaml")
    implemented = (
        set(PATTERNS)
        | {
            "off_domain",
            "pay_unstated",
            "commission_only",
            "equity_only",
            "employment_type_not_allowed",
            "not_remote",
            "employer_unverifiable",
            "source_url_invalid",
            "source_blocked",
            "source_not_approved",
        }
    )
    hard_rejections = set(policy["hard_rejections"])
    assert hard_rejections <= implemented
    assert hard_rejections <= set(catalogue["rejection_reasons"])


def test_policy_scope_settings_are_explicit_and_supported():
    policy = load_job_search_policy()
    assert policy["workplace"] == "remote_only"
    assert policy["compensation"]["require_amount"] is True
    assert policy["compensation"]["require_currency"] is True
    assert policy["compensation"]["require_period"] is True
    assert policy["compensation"]["reject_unspecified"] is True
    assert set(policy["compensation"]["accepted_types"]) == {"salary", "hourly"}
