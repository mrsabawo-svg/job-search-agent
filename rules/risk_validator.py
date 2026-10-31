import re
PATTERNS={
 'paid_to_apply':r'(?i)\\b(pay|payment|fee)\\b.{0,30}\\b(apply|application|access)\\b',
 'crypto_trading_scheme':r'(?i)\\b(crypto|forex)\\b.{0,50}\\b(trader|investment|signals)\\b',
 'network_marketing':r'(?i)\\b(network marketing|multi[- ]level marketing|MLM)\\b',
 'vague_data_entry':r'(?i)\\b(remote data entry|data entry clerk)\\b',
 'generic_virtual_assistant':r'(?i)\\b(virtual assistant|personal assistant)\\b'}
def detect_risk(text: str) -> list[str]:
    return [code for code,pattern in PATTERNS.items() if re.search(pattern,text or '')]
