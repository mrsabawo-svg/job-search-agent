import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from domain.decision_states import DecisionState
from schema.job_record import Compensation, JobRecord
from schema.validation_result import Evidence, ValidationResult
from workflow.orchestrator import qualify_job

ROOT = Path(__file__).resolve().parents[1]


def sample(name):
    return json.loads((ROOT / "data/samples" / name).read_text())[0]


def test_valid_looking_job_remains_review():
    result = qualify_job(JobRecord.model_validate(sample("valid_jobs.json")))
    assert result.decision == DecisionState.REVIEW
    assert not result.reason_codes


def test_commission_crypto_is_rejected():
    result = qualify_job(JobRecord.model_validate(sample("rejected_jobs.json")))
    assert result.decision == DecisionState.REJECT
    assert "commission_only" in result.reason_codes
    assert "crypto_trading_scheme" in result.reason_codes


def test_salary_requires_all_pay_fields():
    with pytest.raises(ValidationError):
        Compensation.model_validate({"type": "salary", "amount": 80000, "currency": "USD"})


def test_hourly_pay_requires_hour_period():
    with pytest.raises(ValidationError):
        Compensation.model_validate({"type": "hourly", "amount": 40, "currency": "USD", "period": "year"})


def test_salary_rejects_hour_period():
    with pytest.raises(ValidationError):
        Compensation.model_validate({"type": "salary", "amount": 80000, "currency": "USD", "period": "hour"})


def test_currency_must_be_uppercase_three_letters():
    with pytest.raises(ValidationError):
        Compensation.model_validate({"type": "salary", "amount": 80000, "currency": "usd", "period": "year"})


@pytest.mark.parametrize("field,value", [
    ("source", "unapproved_board"),
    ("employment_type", "part_time"),
    ("workplace", "mostly_remote"),
])
def test_job_rejects_unknown_policy_values(field, value):
    job = sample("valid_jobs.json")
    job[field] = value
    with pytest.raises(ValidationError):
        JobRecord.model_validate(job)


def test_job_rejects_blank_title():
    job = sample("valid_jobs.json")
    job["title"] = "   "
    with pytest.raises(ValidationError):
        JobRecord.model_validate(job)


def test_result_requires_positive_policy_version():
    with pytest.raises(ValidationError):
        ValidationResult.model_validate({"job_id": "job-1", "decision": "REVIEW", "policy_version": 0})


def test_evidence_requires_valid_source_and_timestamp():
    with pytest.raises(ValidationError):
        Evidence.model_validate({"field": "workplace", "value": "remote", "source_url": "bad-url", "captured_at": "bad-time"})
