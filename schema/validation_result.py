from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from domain.decision_states import DecisionState


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str = Field(min_length=1)
    value: str = Field(min_length=1)
    source_url: HttpUrl
    captured_at: datetime


class ValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_id: str = Field(min_length=1)
    decision: DecisionState
    reason_codes: list[str] = Field(default_factory=list)
    review_flags: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    policy_version: int = Field(default=1, ge=1)
