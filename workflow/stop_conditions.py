from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite

from policy_loader import load_job_search_policy


@dataclass(frozen=True)
class StopLimits:
    max_runtime_minutes: int = 45
    max_sources_per_run: int = 8
    max_discovery_attempts: int = 120
    max_unique_candidates: int = 250
    max_validation_attempts: int = 250
    max_application_attempts: int = 0
    max_browser_sessions: int = 2
    max_retries_per_operation: int = 2
    max_llm_calls: int = 100
    max_llm_cost_usd: float = 2.0

    @classmethod
    def from_policy(cls) -> "StopLimits":
        values = load_job_search_policy().get("stop_conditions")
        if not isinstance(values, dict):
            raise ValueError("Policy requires stop_conditions mapping")
        try:
            return cls(**values)
        except TypeError as exc:
            raise ValueError("Policy stop_conditions do not match supported limits") from exc


def stop_reasons(
    *,
    discovery_attempts: int = 0,
    candidates: int = 0,
    validation_attempts: int = 0,
    application_attempts: int = 0,
    sources_attempted: int = 0,
    browser_sessions: int = 0,
    retries_for_operation: int = 0,
    llm_calls: int = 0,
    llm_cost_usd: float = 0.0,
    started_at: datetime | None = None,
    now: datetime | None = None,
    limits: StopLimits | None = None,
) -> list[str]:
    limits = limits or StopLimits.from_policy()
    counters = {
        "discovery_attempts": discovery_attempts,
        "candidates": candidates,
        "validation_attempts": validation_attempts,
        "application_attempts": application_attempts,
        "sources_attempted": sources_attempted,
        "browser_sessions": browser_sessions,
        "retries_for_operation": retries_for_operation,
        "llm_calls": llm_calls,
    }
    if any(value < 0 for value in counters.values()):
        raise ValueError("Stop-condition counters cannot be negative")
    if not isfinite(llm_cost_usd) or llm_cost_usd < 0:
        raise ValueError("LLM cost must be a finite non-negative value")

    reasons = []
    if sources_attempted >= limits.max_sources_per_run:
        reasons.append("source_budget_exhausted")
    if discovery_attempts >= limits.max_discovery_attempts:
        reasons.append("discovery_budget_exhausted")
    if candidates >= limits.max_unique_candidates:
        reasons.append("candidate_budget_exhausted")
    if validation_attempts >= limits.max_validation_attempts:
        reasons.append("validation_budget_exhausted")
    if application_attempts > limits.max_application_attempts:
        reasons.append("application_attempt_limit_exceeded")
    if browser_sessions >= limits.max_browser_sessions:
        reasons.append("browser_session_budget_exhausted")
    if retries_for_operation >= limits.max_retries_per_operation:
        reasons.append("retry_limit_reached")
    if llm_calls >= limits.max_llm_calls:
        reasons.append("llm_call_budget_exhausted")
    if llm_cost_usd >= limits.max_llm_cost_usd:
        reasons.append("llm_cost_budget_exhausted")

    if started_at is not None:
        current_time = now or datetime.now(timezone.utc)
        if started_at.tzinfo is None or started_at.utcoffset() is None:
            raise ValueError("started_at must include a timezone")
        if current_time.tzinfo is None or current_time.utcoffset() is None:
            raise ValueError("now must include a timezone")
        elapsed = (current_time - started_at).total_seconds()
        if elapsed >= limits.max_runtime_minutes * 60:
            reasons.append("runtime_budget_exhausted")

    return reasons


def budget_exhausted(**kwargs) -> bool:
    return bool(stop_reasons(**kwargs))
