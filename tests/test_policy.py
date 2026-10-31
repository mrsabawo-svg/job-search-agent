from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
def load(path):
    return yaml.safe_load((ROOT/path).read_text(encoding='utf-8'))
def test_policy_scope():
    p=load('policy/job_search_policy.yaml')
    assert p['workplace']=='remote_only' and set(p['employment_types'])=={'full_time','contract'}
    assert p['compensation']['reject_unspecified'] is True and p['stop_conditions']['max_application_attempts']==0
def test_reason_codes():
    r=load('policy/rejection_reasons.yaml')['rejection_reasons']
    assert {'off_domain','pay_unstated','commission_only','equity_only','scam_signal','duplicate','expired'} <= set(r)
