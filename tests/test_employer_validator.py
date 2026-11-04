import pytest

from rules.employer_validator import validate_employer


@pytest.mark.parametrize("domain", [
    "company.example",
    "sub.company.example",
])
def test_accepts_well_formed_employer_domain(domain):
    assert validate_employer("Example Company", domain) == []


@pytest.mark.parametrize("domain", [
    "https://company.example",
    "company.example/jobs",
    "company example",
    "-company.example",
    "company..example",
    "localhost",
    "company.example:443",
])
def test_rejects_malformed_employer_domain(domain):
    assert validate_employer("Example Company", domain) == ["employer_unverifiable"]


def test_rejects_missing_employer_identity():
    assert validate_employer("Example Company", None) == ["employer_unverifiable"]



def test_identity_requirement_can_be_disabled_by_explicit_policy():
    assert validate_employer(
        "", None, require_verifiable_identity=False, require_official_domain=True
    ) == []


def test_official_domain_requirement_can_be_disabled_by_explicit_policy():
    assert validate_employer(
        "Example Company", None,
        require_verifiable_identity=True, require_official_domain=False
    ) == []


def test_required_official_domain_is_enforced_by_policy():
    assert validate_employer(
        "Example Company", None,
        require_verifiable_identity=True, require_official_domain=True
    ) == ["employer_unverifiable"]
