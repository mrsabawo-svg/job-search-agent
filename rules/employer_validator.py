import re


DOMAIN_PATTERN = re.compile(
    r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\\.)+[a-z]{2,63}$"
)


def validate_employer(
    employer_name: str,
    employer_domain: str | None,
    *,
    require_verifiable_identity: bool = True,
    require_official_domain: bool = True,
) -> list[str]:
    if not require_verifiable_identity:
        return []
    if not employer_name or not employer_name.strip():
        return ["employer_unverifiable"]
    if not employer_domain:
        return ["employer_unverifiable"] if require_official_domain else []

    domain = employer_domain.strip().lower().rstrip(".")
    if not DOMAIN_PATTERN.fullmatch(domain):
        return ["employer_unverifiable"]

    return []
