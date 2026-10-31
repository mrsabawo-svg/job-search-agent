from datetime import datetime, timedelta, timezone

import pytest

from workflow.stop_conditions import StopLimits, budget_exhausted, stop_reasons


def test_limits_load_from_authoritative_policy():
    limits = StopLimits.from_policy()
    assert limits.max_application_attempts == 0
    assert limits.max_sources_per_run == 8
    assert limits.max_llm_cost_usd == 2.0


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        ({"sources_attempted": 8}, "source_budget_exhausted"),
        ({"discovery_attempts": 120}, "discovery_budget_exhausted"),
        ({"candidates": 250}, "candidate_budget_exhausted"),
        ({"validation_attempts": 250}, "validation_budget_exhausted"),
        ({"application_attempts": 1}, "application_attempt_limit_exceeded"),
        ({"browser_sessions": 2}, "browser_session_budget_exhausted"),
        ({"retries_for_operation": 2}, "retry_limit_reached"),
        ({"llm_calls": 100}, "llm_call_budget_exhausted"),
        ({"llm_cost_usd": 2.0}, "llm_cost_budget_exhausted"),
    ],
)
def test_each_stop_limit_is_enforced(kwargs, expected):
    assert expected in stop_reasons(**kwargs)
    assert budget_exhausted(**kwargs)


def test_runtime_limit_is_enforced_with_timezone_aware_clock():
    start = datetime(2026, 10, 31, 10, 0, tzinfo=timezone.utc)
    current = start + timedelta(minutes=45)
    assert "runtime_budget_exhausted" in stop_reasons(started_at=start, now=current)


def test_negative_counters_are_rejected():
    with pytest.raises(ValueError):
        stop_reasons(discovery_attempts=-1)


def test_naive_runtime_timestamp_is_rejected():
    with pytest.raises(ValueError):
        stop_reasons(started_at=datetime(2026, 10, 31, 10, 0))
