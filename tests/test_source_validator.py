import pytest

from domain.source_types import SourceType
from rules.source_validator import validate_source


def test_enabled_greenhouse_source_and_host_are_accepted():
    assert validate_source(
        SourceType.GREENHOUSE,
        "https://boards.greenhouse.io/acme/jobs/123",
    ) == []


def test_enabled_source_rejects_unrelated_host():
    assert validate_source(
        SourceType.GREENHOUSE,
        "https://greenhouse.io.attacker.example/jobs/123",
    ) == ["source_not_approved"]


def test_disabled_job_board_is_rejected():
    assert validate_source(
        SourceType.REMOTE_OK,
        "https://remoteok.com/remote-jobs/123",
    ) == ["source_not_approved"]


def test_source_id_must_match_host_policy():
    assert validate_source(
        SourceType.LEVER,
        "https://boards.greenhouse.io/acme/jobs/123",
    ) == ["source_not_approved"]


def test_http_source_url_is_rejected():
    assert validate_source(
        SourceType.GREENHOUSE,
        "http://boards.greenhouse.io/acme/jobs/123",
    ) == ["source_url_invalid"]


def test_blocked_watchlist_domain_is_rejected():
    assert validate_source(
        SourceType.OTHER,
        "https://example.com/job/123",
    ) == ["source_blocked"]


def test_domain_suffix_spoofing_does_not_match_approved_host():
    assert validate_source(
        SourceType.GREENHOUSE,
        "https://greenhouse.io.attacker.example/job/123",
    ) == ["source_not_approved"]
