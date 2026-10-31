from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]


class PolicyConfigurationError(ValueError):
    """Raised when policy configuration is missing or unsafe to interpret."""


def _load_yaml(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = yaml.safe_load(handle)
    except (OSError, yaml.YAMLError) as exc:
        raise PolicyConfigurationError(f"Unable to load policy file: {relative_path}") from exc
    if not isinstance(value, dict):
        raise PolicyConfigurationError(f"Policy file must contain a mapping: {relative_path}")
    return value


def load_source_policy() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    approved_data = _load_yaml("sources/approved_sources.yaml")
    watchlist_data = _load_yaml("sources/watchlist.yaml")
    approved = approved_data.get("approved_sources")
    watchlist = watchlist_data.get("watchlist")
    if not isinstance(approved, list) or not isinstance(watchlist, list):
        raise PolicyConfigurationError("Source policy requires approved_sources and watchlist lists")

    for entry in approved:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str):
            raise PolicyConfigurationError("Each approved source requires an id")
        if not isinstance(entry.get("enabled"), bool):
            raise PolicyConfigurationError(f"Source {entry.get('id')} requires an enabled boolean")
        if not isinstance(entry.get("domains"), list) or not entry["domains"]:
            raise PolicyConfigurationError(f"Source {entry.get('id')} requires at least one domain")
        if any(not isinstance(domain, str) or not domain.strip() for domain in entry["domains"]):
            raise PolicyConfigurationError(f"Source {entry.get('id')} contains an invalid domain")

    for entry in watchlist:
        if not isinstance(entry, dict) or not isinstance(entry.get("domain"), str):
            raise PolicyConfigurationError("Each watchlist entry requires a domain")
        if entry.get("status") not in {"blocked", "review"}:
            raise PolicyConfigurationError("Watchlist status must be blocked or review")

    return approved, watchlist
