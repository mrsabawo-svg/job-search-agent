import re


PATTERNS = {
    "paid_to_apply": r"(?i)\b(pay|payment|fee)\b.{0,30}\b(apply|application|access)\b",
    "pay_to_start": r"(?i)\b(registration|training|onboarding|equipment)\s+(?:fee|payment)\b",
    "crypto_trading_scheme": r"(?i)\b(crypto|forex)\b.{0,50}\b(trader|investment|signals)\b",
    "network_marketing": r"(?i)\b(network marketing|multi[- ]level marketing|MLM)\b",
    "vague_data_entry": r"(?i)\b(remote data entry|data entry clerk)\b",
    "generic_virtual_assistant": r"(?i)\b(virtual assistant|personal assistant)\b",
    "agency_posting": (
        r"(?i)\b(we are a recruitment agency|staffing agency|recruitment consultancy|"
        r"on behalf of our client|our client is hiring)\b"
    ),
    "dm_only_hiring": r"(?i)\b(dm|direct message)\s+(me|us|to apply)\b",
    "whatsapp_hiring": (
        r"(?i)\b(whats ?app|wa\.me)\b.{0,50}\b(apply|message|contact|"
        r"send (?:your )?(?:cv|resume))\b"
    ),
}


def detect_risk(text: str) -> list[str]:
    content = text or ""
    return [code for code, pattern in PATTERNS.items() if re.search(pattern, content)]
