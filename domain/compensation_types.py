from enum import StrEnum
class CompensationType(StrEnum):
    SALARY='salary'
    HOURLY='hourly'
    COMMISSION='commission'
    EQUITY='equity'
    UNSPECIFIED='unspecified'
class PayPeriod(StrEnum):
    HOUR='hour'
    MONTH='month'
    YEAR='year'
