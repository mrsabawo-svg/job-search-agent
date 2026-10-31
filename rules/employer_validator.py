def validate_employer(employer_name: str, employer_domain: str | None) -> list[str]:
    if not employer_name.strip() or not employer_domain: return ['employer_unverifiable']
    domain=employer_domain.strip().lower()
    if domain.startswith(('http://','https://')) or '/' in domain: return ['employer_unverifiable']
    return []
