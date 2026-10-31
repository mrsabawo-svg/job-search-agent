from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from typing import Optional
from domain.compensation_types import CompensationType, PayPeriod
from domain.job_categories import JobCategory
class Compensation(BaseModel):
    model_config=ConfigDict(extra='forbid')
    type: CompensationType
    amount: Optional[float]=Field(default=None,gt=0)
    currency: Optional[str]=None
    period: Optional[PayPeriod]=None
class JobRecord(BaseModel):
    model_config=ConfigDict(extra='forbid')
    job_id: str
    title: str
    employer_name: str
    employer_domain: Optional[str]=None
    source: str
    source_url: HttpUrl
    application_url: Optional[HttpUrl]=None
    category: JobCategory
    employment_type: str
    workplace: str
    eligible_locations: list[str]=Field(default_factory=list)
    compensation: Compensation
    description_text: str=''
