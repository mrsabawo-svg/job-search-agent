from urllib.parse import urlsplit

from domain.source_types import SourceType
from policy_loader import load_source_policy


def _host_matches(host: str, domain: str) -> bool:
    host = host.lower().rstrip(".")
    domain = domain.lower().strip().rstrip(".")
    return host == domain or host.endswith("." + domain)


def validate_source(source: SourceType, source_url: str) -> list[str]:
    approved, watchlist = load_source_policy()
    parsed = urlsplit(str(source_url))
    host = (parsed.hostname or "").lower().rstrip(".")
    if parsed.scheme.lower() != "https" or not host:
        return ["source_url_invalid"]

    for entry in watchlist:
        if _host_matches(host, entry["domain"]):
            if entry["status"] == "blocked":
                return ["source_blocked"]
            return ["source_requires_review"]

    for entry in approved:
        if entry["id"] != source.value or not entry["enabled"]:
            continue
        if any(_host_matches(host, domain) for domain in entry["domains"]):
            return []

    return ["source_not_approved"]
