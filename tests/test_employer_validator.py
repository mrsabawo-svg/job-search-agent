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
