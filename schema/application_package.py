from pydantic import BaseModel, ConfigDict, Field


class ApplicationPackage(BaseModel):
    """Prepared materials only; approval and submission authority live in workflow state."""

    model_config = ConfigDict(extra="forbid")

    job_id: str = Field(min_length=1)
    resume_variant_id: str = Field(min_length=1)
    tailored_resume_text: str = Field(min_length=1)
    cover_letter_text: str = ""
    applicant_facts_used: list[str] = Field(default_factory=list)
    unresolved_questions: list[str] = Field(default_factory=list)
