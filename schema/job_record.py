from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator

from domain.compensation_types import CompensationType, PayPeriod
from domain.job_categories import JobCategory
from domain.source_types import SourceType


class Compensation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: CompensationType
    amount: float | None = Field(default=None, gt=0)
    currency: str | None = None
    period: PayPeriod | None = None

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, value):
        if value is not None and (len(value) != 3 or not value.isalpha() or not value.isupper()):
            raise ValueError("currency must be a three-letter uppercase code")
        return value

    @model_validator(mode="after")
    def validate_period_compatibility(self):
        if self.type == CompensationType.HOURLY and self.period not in (None, PayPeriod.HOUR):
            raise ValueError("hourly compensation must use the hour pay period")
        if self.type == CompensationType.SALARY and self.period == PayPeriod.HOUR:
            raise ValueError("salary compensation must use month or year pay period")
        return self


class JobRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    job_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    employer_name: str = Field(min_length=1)
    employer_domain: str | None = None
    source: SourceType
    source_url: HttpUrl
    application_url: HttpUrl | None = None
    category: JobCategory
    employment_type: Literal["full_time", "contract"]
    workplace: Literal["remote", "hybrid", "onsite", "unknown"]
    eligible_locations: list[str] = Field(default_factory=list)
    compensation: Compensation
    description_text: str = ""

    @field_validator("job_id", "title", "employer_name")
    @classmethod
    def reject_blank_required_text(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("required text must not be blank")
        return value

    @field_validator("eligible_locations")
    @classmethod
    def normalize_eligible_locations(cls, values):
        normalized = [value.strip() for value in values if value.strip()]
        return list(dict.fromkeys(normalized))
