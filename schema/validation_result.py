from pydantic import BaseModel, Field
from domain.decision_states import DecisionState
class Evidence(BaseModel):
    field: str
    value: str
    source_url: str
    captured_at: str
class ValidationResult(BaseModel):
    job_id: str
    decision: DecisionState
    reason_codes: list[str]=Field(default_factory=list)
    review_flags: list[str]=Field(default_factory=list)
    evidence: list[Evidence]=Field(default_factory=list)
    policy_version: int=1
