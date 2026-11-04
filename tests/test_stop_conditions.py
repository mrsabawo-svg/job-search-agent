from datetime import datetime, timedelta, timezone

import pytest

from workflow.stop_conditions import StopConditionReached, StopLimits, budget_exhausted, enforce_run_limits, stop_reasons


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



def test_execution_guard_raises_before_side_effect_when_budget_is_reached():
    with pytest.raises(StopConditionReached) as exc:
        enforce_run_limits(discovery_attempts=120)
    assert exc.value.reasons == ("discovery_budget_exhausted",)


def test_execution_guard_allows_work_below_all_limits():
    assert enforce_run_limits() is None


def test_application_attempts_are_blocked_by_zero_limit():
    with pytest.raises(StopConditionReached) as exc:
        enforce_run_limits(application_attempts=1)
    assert "application_attempt_limit_exceeded" in exc.value.reasons


def test_stop_policy_rejects_missing_or_unknown_limits(monkeypatch):
    import workflow.stop_conditions as stop_module

    monkeypatch.setattr(stop_module, "load_job_search_policy", lambda: {
        "stop_conditions": {"max_application_attempts": 0, "unexpected": 1}
    })
    with pytest.raises(ValueError, match="keys mismatch"):
        StopLimits.from_policy()


def test_stop_policy_cannot_enable_application_attempts(monkeypatch):
    import workflow.stop_conditions as stop_module

    values = {
        "max_runtime_minutes": 45,
        "max_sources_per_run": 8,
        "max_discovery_attempts": 120,
        "max_unique_candidates": 250,
        "max_validation_attempts": 250,
        "max_application_attempts": 1,
        "max_browser_sessions": 2,
        "max_retries_per_operation": 2,
        "max_llm_calls": 100,
        "max_llm_cost_usd": 2.0,
    }
    monkeypatch.setattr(stop_module, "load_job_search_policy", lambda: {"stop_conditions": values})
    with pytest.raises(ValueError, match="prohibit application attempts"):
        StopLimits.from_policy()


def test_boolean_counter_is_not_accepted_as_integer():
    with pytest.raises(ValueError, match="non-negative integers"):
        stop_reasons(discovery_attempts=True)


def test_non_finite_llm_cost_is_rejected():
    with pytest.raises(ValueError, match="finite"):
        stop_reasons(llm_cost_usd=float("nan"))
