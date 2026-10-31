import json
from pathlib import Path
from domain.decision_states import DecisionState
from schema.job_record import JobRecord
from workflow.orchestrator import qualify_job
ROOT=Path(__file__).resolve().parents[1]
def sample(name): return json.loads((ROOT/'data/samples'/name).read_text())[0]
def test_valid_looking_job_remains_review():
    result=qualify_job(JobRecord.model_validate(sample('valid_jobs.json')))
    assert result.decision==DecisionState.REVIEW and not result.reason_codes
def test_commission_crypto_is_rejected():
    result=qualify_job(JobRecord.model_validate(sample('rejected_jobs.json')))
    assert result.decision==DecisionState.REJECT and 'commission_only' in result.reason_codes and 'crypto_trading_scheme' in result.reason_codes
