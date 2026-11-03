import pytest

import policy_loader
from domain.source_types import SourceType
from policy_loader import PolicyConfigurationError
from rules import source_validator
from rules.source_validator import validate_source


def write_source_policy_root(root, approved_sources, *, approved_path="sources/approved_sources.yaml"):
    (root / "policy").mkdir(parents=True, exist_ok=True)
    (root / "sources").mkdir(parents=True, exist_ok=True)
    (root / "policy" / "job_search_policy.yaml").write_text(
        "version: 1\\n"
        "target_categories: [software_engineering]\\n"
        "employment_types: [full_time]\\n"
        "workplace: remote_only\\n"
        "compensation: {accepted_types: [salary], require_amount: true, require_currency: true, require_period: true, reject_unspecified: true}\\n"
        f"sources: {{employer_ats_only_by_default: true, approved_source_file: '{approved_path}', watchlist_file: 'sources/watchlist.yaml'}}\\n",
        encoding="utf-8",
    )
    (root / approved_path).parent.mkdir(parents=True, exist_ok=True)
    (root / approved_path).write_text(approved_sources, encoding="utf-8")
    (root / "sources" / "watchlist.yaml").write_text("watchlist: []\\n", encoding="utf-8")


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


def test_enabled_job_board_requires_explicit_approval(monkeypatch):
    monkeypatch.setattr(source_validator, "load_job_search_policy", lambda: {
        "sources": {"employer_ats_only_by_default": True}
    })
    monkeypatch.setattr(source_validator, "load_source_policy", lambda: (
        [{
            "id": "remoteok",
            "type": "job_board",
            "enabled": True,
            "explicit_approval": False,
            "domains": ["remoteok.com"],
        }],
        [],
    ))
    assert validate_source(
        SourceType.REMOTE_OK,
        "https://remoteok.com/remote-jobs/123",
    ) == ["source_not_approved"]


def test_explicitly_approved_enabled_job_board_is_allowed(monkeypatch):
    monkeypatch.setattr(source_validator, "load_job_search_policy", lambda: {
        "sources": {"employer_ats_only_by_default": True}
    })
    monkeypatch.setattr(source_validator, "load_source_policy", lambda: (
        [{
            "id": "remoteok",
            "type": "job_board",
            "enabled": True,
            "explicit_approval": True,
            "domains": ["remoteok.com"],
        }],
        [],
    ))
    assert validate_source(
        SourceType.REMOTE_OK,
        "https://remoteok.com/remote-jobs/123",
    ) == []


def test_source_registry_rejects_duplicate_ids(tmp_path, monkeypatch):
    (tmp_path / "sources").mkdir()
    (tmp_path / "sources" / "approved_sources.yaml").write_text(
        "approved_sources:\n"
        "  - {id: greenhouse, type: employer_ats, enabled: true, domains: [greenhouse.io]}\n"
        "  - {id: greenhouse, type: employer_ats, enabled: true, domains: [boards.greenhouse.io]}\n",
        encoding="utf-8",
    )
    (tmp_path / "sources" / "watchlist.yaml").write_text("watchlist: []\n", encoding="utf-8")
    monkeypatch.setattr(policy_loader, "ROOT", tmp_path)
    with pytest.raises(PolicyConfigurationError, match="Duplicate approved source id"):
        policy_loader.load_source_policy()


def test_job_board_registry_requires_explicit_approval_setting(tmp_path, monkeypatch):
    (tmp_path / "sources").mkdir()
    (tmp_path / "sources" / "approved_sources.yaml").write_text(
        "approved_sources:\n"
        "  - {id: remoteok, type: job_board, enabled: false, domains: []}\n",
        encoding="utf-8",
    )
    (tmp_path / "sources" / "watchlist.yaml").write_text("watchlist: []\n", encoding="utf-8")
    monkeypatch.setattr(policy_loader, "ROOT", tmp_path)
    with pytest.raises(PolicyConfigurationError, match="explicit_approval"):
        policy_loader.load_source_policy()
