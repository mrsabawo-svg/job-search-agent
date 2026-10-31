from pydantic import BaseModel, Field
class ApplicationPackage(BaseModel):
    """Prepared materials only; this model does not authorize submission."""
    job_id: str
    resume_variant_id: str
    tailored_resume_text: str
    cover_letter_text: str=''
    applicant_facts_used: list[str]=Field(default_factory=list)
    unresolved_questions: list[str]=Field(default_factory=list)
    human_approved: bool=False
    submission_authorized: bool=False
