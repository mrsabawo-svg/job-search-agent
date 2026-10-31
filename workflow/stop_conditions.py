from dataclasses import dataclass
@dataclass(frozen=True)
class StopLimits:
    max_runtime_minutes:int=45
    max_sources_per_run:int=8
    max_discovery_attempts:int=120
    max_unique_candidates:int=250
    max_validation_attempts:int=250
    max_application_attempts:int=0
    max_browser_sessions:int=2
    max_retries_per_operation:int=2
    max_llm_calls:int=100
    max_llm_cost_usd:float=2.0
def budget_exhausted(*,discovery_attempts:int,candidates:int,validation_attempts:int,application_attempts:int,limits:StopLimits=StopLimits())->bool:
    return discovery_attempts>=limits.max_discovery_attempts or candidates>=limits.max_unique_candidates or validation_attempts>=limits.max_validation_attempts or application_attempts>limits.max_application_attempts
