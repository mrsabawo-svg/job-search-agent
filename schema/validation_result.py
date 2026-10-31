from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator

from domain.decision_states import DecisionState


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    field: str = Field(min_length=1)
    value: str = Field(min_length=1)
    source_url: HttpUrl
    captured_at: datetime

    @field_validator("field", "value")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("evidence text must not be blank")
        return value

    @field_validator("captured_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("captured_at must include a timezone")
        return value


class ValidationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_id: str = Field(min_length=1)
    decision: DecisionState
    reason_codes: list[str] = Field(default_factory=list)
    review_flags: list[str] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    policy_version: int = Field(default=1, ge=1)

    @field_validator("job_id")
    @classmethod
    def normalize_job_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("job_id must not be blank")
        return value

    @field_validator("reason_codes", "review_flags")
    @classmethod
    def validate_codes(cls, values: list[str]) -> list[str]:
        normalized = []
        for value in values:
            code = value.strip()
            if not code:
                raise ValueError("reason and review codes must not be blank")
            if code in normalized:
                raise ValueError("reason and review codes must be unique")
            normalized.append(code)
        return normalized

    @model_validator(mode="after")
    def validate_decision_consistency(self):
        if self.decision == DecisionState.REJECT and not self.reason_codes:
            raise ValueError("REJECT requires at least one reason code")
        if self.decision == DecisionState.ACCEPT:
            if self.reason_codes:
                raise ValueError("ACCEPT cannot contain rejection reason codes")
            if self.review_flags:
                raise ValueError("ACCEPT cannot contain unresolved review flags")
            if not self.evidence:
                raise ValueError("ACCEPT requires supporting evidence")
        return self
