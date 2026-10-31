import json
from pathlib import Path

import pytest
from pydantic import ValidationError

import rules.policy_validator as policy_validator
from policy_loader import PolicyConfigurationError, load_job_search_policy
from schema.job_record import Compensation, JobRecord

ROOT = Path(__file__).resolve().parents[1]


def sample_job():
    return json.loads((ROOT / "data/samples/valid_jobs.json").read_text())[0]


def test_compensation_schema_allows_policy_assessed_missing_fields():
    compensation = Compensation.model_validate({"type": "salary", "amount": 80000, "currency": "USD"})
    assert compensation.period is None


def test_compensation_schema_still_rejects_invalid_currency_and_period():
    with pytest.raises(ValidationError):
        Compensation.model_validate({"type": "salary", "amount": 80000, "currency": "usd", "period": "year"})
    with pytest.raises(ValidationError):
        Compensation.model_validate({"type": "hourly", "amount": 40, "currency": "USD", "period": "year"})


@pytest.mark.parametrize("field", ["amount", "currency", "period"])
def test_enabled_pay_completeness_setting_is_enforced(field, monkeypatch):
    raw = sample_job()
    raw["compensation"].pop(field)
    job = JobRecord.model_validate(raw)

    policy = load_job_search_policy()
    monkeypatch.setattr(policy_validator, "load_job_search_policy", lambda: policy)
    assert "pay_unstated" in policy_validator.validate_policy_scope(job)


@pytest.mark.parametrize("field", ["require_amount", "require_currency", "require_period"])
def test_disabling_pay_completeness_setting_changes_decision(field, monkeypatch):
    raw = sample_job()
    raw["compensation"].pop(field.removeprefix("require_"))
    job = JobRecord.model_validate(raw)

    policy = load_job_search_policy()
    policy["compensation"][field] = False
    monkeypatch.setattr(policy_validator, "load_job_search_policy", lambda: policy)
    assert "pay_unstated" not in policy_validator.validate_policy_scope(job)


def test_policy_loader_rejects_non_boolean_compensation_setting(monkeypatch, tmp_path):
    policy_path = tmp_path / "policy" / "job_search_policy.yaml"
    policy_path.parent.mkdir()
    policy_path.write_text(
        "version: 1\ntarget_categories: [software_engineering]\nemployment_types: [full_time]\n"
        "workplace: remote_only\ncompensation:\n  accepted_types: [salary]\n"
        "  require_amount: yes\n  require_currency: true\n  require_period: true\n"
        "  reject_unspecified: true\n",
        encoding="utf-8",
    )
    monkeypatch.setattr("policy_loader.ROOT", tmp_path)
    with pytest.raises(PolicyConfigurationError):
        load_job_search_policy()


def test_unspecified_pay_rejection_is_policy_controlled(monkeypatch):
    raw = sample_job()
    raw["compensation"] = {"type": "unspecified"}
    job = JobRecord.model_validate(raw)
    policy = load_job_search_policy()
    monkeypatch.setattr(policy_validator, "load_job_search_policy", lambda: policy)
    assert "pay_unstated" in policy_validator.validate_policy_scope(job)

    policy["compensation"]["reject_unspecified"] = False
    assert "pay_unstated" not in policy_validator.validate_policy_scope(job)
