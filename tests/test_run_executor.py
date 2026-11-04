from datetime import datetime, timedelta, timezone

import pytest

from workflow.run_executor import RunExecutor
from workflow.stop_conditions import StopConditionReached, StopLimits


def small_limits(**overrides):
    values = {
        "max_runtime_minutes": 45,
        "max_sources_per_run": 2,
        "max_discovery_attempts": 2,
        "max_unique_candidates": 2,
        "max_validation_attempts": 2,
        "max_application_attempts": 0,
        "max_browser_sessions": 2,
        "max_retries_per_operation": 2,
        "max_llm_calls": 100,
        "max_llm_cost_usd": 2.0,
    }
    values.update(overrides)
    return StopLimits(**values)


def test_executor_runs_operation_and_reserves_attempt():
    executor = RunExecutor(limits=small_limits())
    assert executor.execute("discovery", lambda: "found") == "found"
    assert executor.counters.discovery_attempts == 1


@pytest.mark.parametrize(
    ("operation", "counter"),
    [
        ("source", "sources_attempted"),
        ("discovery", "discovery_attempts"),
        ("candidate", "candidates"),
        ("validation", "validation_attempts"),
    ],
)
def test_each_operation_budget_blocks_before_callback(operation, counter):
    executor = RunExecutor(limits=small_limits(**{
        {
            "source": "max_sources_per_run",
            "discovery": "max_discovery_attempts",
            "candidate": "max_unique_candidates",
            "validation": "max_validation_attempts",
        }[operation]: 1
    }))
    executor.execute(operation, lambda: None)
    called = False

    def side_effect():
        nonlocal called
        called = True

    with pytest.raises(StopConditionReached):
        executor.execute(operation, side_effect)

    assert called is False
    assert getattr(executor.counters, counter) == 1


def test_failed_operation_still_consumes_reserved_attempt():
    executor = RunExecutor(limits=small_limits())

    def fail():
        raise RuntimeError("source failed")

    with pytest.raises(RuntimeError, match="source failed"):
        executor.execute("source", fail)

    assert executor.counters.sources_attempted == 1


def test_expired_run_blocks_operation_before_callback():
    start = datetime(2026, 11, 4, 10, 0, tzinfo=timezone.utc)
    executor = RunExecutor(started_at=start, limits=small_limits())
    called = False

    def side_effect():
        nonlocal called
        called = True

    with pytest.raises(StopConditionReached, match="runtime_budget_exhausted"):
        executor.execute("discovery", side_effect, now=start + timedelta(minutes=45))

    assert called is False
    assert executor.counters.discovery_attempts == 0


@pytest.mark.parametrize("operation", ["application", "browser"])
def test_future_side_effect_boundaries_are_not_exposed(operation):
    executor = RunExecutor(limits=small_limits())
    called = False

    def side_effect():
        nonlocal called
        called = True

    with pytest.raises(StopConditionReached):
        executor.execute(operation, side_effect)

    assert called is False


def test_unknown_operation_is_rejected_without_side_effect():
    executor = RunExecutor(limits=small_limits())
    with pytest.raises(ValueError, match="Unsupported run operation"):
        executor.execute("anything", lambda: pytest.fail("must not run"))


def test_executor_requires_timezone_aware_start():
    with pytest.raises(ValueError, match="timezone"):
        RunExecutor(started_at=datetime(2026, 11, 4, 10, 0), limits=small_limits())


def test_qualification_entrypoint_consumes_validation_budget():
    import json
    from pathlib import Path

    from schema.job_record import JobRecord
    from domain.decision_states import DecisionState

    root = Path(__file__).resolve().parents[1]
    sample = json.loads((root / "data/samples/valid_jobs.json").read_text())[0]
    job = JobRecord.model_validate(sample)
    executor = RunExecutor(limits=small_limits())
    result = executor.qualify_job(job)

    assert result.decision == DecisionState.REVIEW
    assert executor.counters.validation_attempts == 1


def test_qualification_entrypoint_blocks_before_qualifier_when_exhausted(monkeypatch):
    import workflow.orchestrator as orchestrator

    executor = RunExecutor(limits=small_limits(max_validation_attempts=0))
    called = False

    def should_not_qualify(*args, **kwargs):
        nonlocal called
        called = True

    monkeypatch.setattr(orchestrator, "qualify_job", should_not_qualify)
    with pytest.raises(StopConditionReached):
        executor.qualify_job(object())

    assert called is False
    assert executor.counters.validation_attempts == 0
