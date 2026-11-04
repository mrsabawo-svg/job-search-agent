"""Guarded, in-memory execution boundary for Milestone 1.

Counters are run-scoped and count attempted operations. Reserve an attempt before
calling user code so failed attempts still consume budget. Persistence and durable
recovery belong to the later workflow/persistence milestones.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, TypeVar

from workflow.stop_conditions import (
    StopConditionReached,
    StopLimits,
    enforce_run_limits,
)

T = TypeVar("T")


@dataclass
class RunCounters:
    sources_attempted: int = 0
    discovery_attempts: int = 0
    candidates: int = 0
    validation_attempts: int = 0


class RunExecutor:
    """The guarded entrypoint for run-level source, discovery and validation work."""

    def __init__(
        self,
        *,
        started_at: datetime | None = None,
        limits: StopLimits | None = None,
    ) -> None:
        self.started_at = started_at or datetime.now(timezone.utc)
        if self.started_at.tzinfo is None or self.started_at.utcoffset() is None:
            raise ValueError("started_at must include a timezone")
        self.limits = limits or StopLimits.from_policy()
        self.counters = RunCounters()

    def _preflight(self, *, now: datetime | None = None) -> None:
        enforce_run_limits(
            sources_attempted=self.counters.sources_attempted,
            discovery_attempts=self.counters.discovery_attempts,
            candidates=self.counters.candidates,
            validation_attempts=self.counters.validation_attempts,
            started_at=self.started_at,
            now=now,
            limits=self.limits,
        )

    def execute(
        self,
        operation: str,
        action: Callable[[], T],
        *,
        now: datetime | None = None,
    ) -> T:
        """Check budgets, reserve the attempt, then invoke the operation.

        Supported operations are source, discovery, candidate and validation.
        Browser and application execution are intentionally not exposed in v1.
        """
        counter_by_operation = {
            "source": ("sources_attempted", "max_sources_per_run"),
            "discovery": ("discovery_attempts", "max_discovery_attempts"),
            "candidate": ("candidates", "max_unique_candidates"),
            "validation": ("validation_attempts", "max_validation_attempts"),
        }
        if operation not in counter_by_operation:
            if operation == "application":
                raise StopConditionReached(("application_attempts_prohibited",))
            if operation == "browser":
                raise StopConditionReached(("browser_execution_not_in_milestone_1",))
            raise ValueError(f"Unsupported run operation: {operation}")

        self._preflight(now=now)
        counter_name, limit_name = counter_by_operation[operation]
        current = getattr(self.counters, counter_name)
        if current >= getattr(self.limits, limit_name):
            raise StopConditionReached((f"{operation}_budget_exhausted",))

        # Reserve before invoking the callback: exceptions still consume attempts.
        setattr(self.counters, counter_name, current + 1)
        return action()

    def qualify_job(self, job, *, policy_version: int | None = None, now: datetime | None = None):
        """Run deterministic qualification through the validation budget gate."""
        from workflow.orchestrator import qualify_job

        return self.execute(
            "validation",
            lambda: qualify_job(job, policy_version=policy_version),
            now=now,
        )
