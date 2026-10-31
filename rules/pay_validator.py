from schema.job_record import Compensation
from domain.compensation_types import CompensationType
def validate_pay(pay: Compensation) -> list[str]:
    reasons=[]
    if pay.type == CompensationType.COMMISSION: reasons.append('commission_only')
    elif pay.type == CompensationType.EQUITY: reasons.append('equity_only')
    elif pay.type == CompensationType.UNSPECIFIED: reasons.append('pay_unstated')
    if pay.type in (CompensationType.SALARY, CompensationType.HOURLY) and (pay.amount is None or not pay.currency or not pay.period): reasons.append('pay_unstated')
    return reasons
