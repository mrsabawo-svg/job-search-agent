from pathlib import Path

import yaml

from domain.compensation_types import CompensationType
from schema.job_record import Compensation, JobRecord
from rules.policy_validator import validate_policy_scope

ROOT = Path(__file__).resolve().parents[1]


def valid_job():
    import json
    return JobRecord.model_validate(json.loads((ROOT / "data/samples/valid_jobs.json").read_text())[0])


def test_policy_categories_match_domain_taxonomy():
    from domain.job_categories import JobCategory
    policy = yaml.safe_load((ROOT / "policy/job_search_policy.yaml").read_text())
    assert {item.value for item in JobCategory} == set(policy["target_categories"])


def test_valid_job_matches_policy_scope():
    assert validate_policy_scope(valid_job()) == []


def test_hybrid_job_is_rejected_by_policy_scope():
    job = valid_job().model_copy(update={"workplace": "hybrid"})
    assert "not_remote" in validate_policy_scope(job)


def test_employment_type_outside_policy_is_rejected():
    job = valid_job().model_copy(update={"employment_type": "part_time"})
    assert "employment_type_not_allowed" in validate_policy_scope(job)


def test_category_outside_policy_is_rejected():
    job = valid_job().model_copy(update={"category": "marketing"})
    assert "off_domain" in validate_policy_scope(job)


def test_compensation_type_outside_policy_is_rejected():
    commission = Compensation.model_construct(
        type=CompensationType.COMMISSION,
        amount=None,
        currency=None,
        period=None,
    )
    job = valid_job().model_copy(update={"compensation": commission})
    assert "pay_unstated" in validate_policy_scope(job)
