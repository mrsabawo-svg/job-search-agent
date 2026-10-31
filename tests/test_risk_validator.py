import pytest

from rules.risk_validator import detect_risk


@pytest.mark.parametrize(
    ("description", "expected_code"),
    [
        ("We are a recruitment agency hiring for our client.", "agency_posting"),
        ("On behalf of our client, we are hiring a backend engineer.", "agency_posting"),
        ("DM us to apply for this remote role.", "dm_only_hiring"),
        ("Send your CV to our WhatsApp contact to apply.", "whatsapp_hiring"),
        ("A registration fee is required before onboarding.", "pay_to_start"),
        ("Pay an application fee to access the opportunity.", "paid_to_apply"),
    ],
)
def test_detects_high_risk_hiring_language(description, expected_code):
    assert expected_code in detect_risk(description)


def test_normal_engineering_description_has_no_risk_match():
    description = (
        "Build and maintain backend APIs, write automated tests, "
        "participate in code reviews and document technical decisions."
    )
    assert detect_risk(description) == []
