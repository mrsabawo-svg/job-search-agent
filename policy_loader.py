from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parent


class PolicyConfigurationError(ValueError):
    """Raised when policy configuration is missing or unsafe to interpret."""


class _UniqueKeySafeLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(loader: _UniqueKeySafeLoader, node: yaml.MappingNode, deep: bool = False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "unhashable mapping key",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    _construct_unique_mapping,
)


def _load_yaml(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = yaml.load(handle, Loader=_UniqueKeySafeLoader)
    except (OSError, yaml.YAMLError) as exc:
        raise PolicyConfigurationError(f"Unable to load policy file: {relative_path}") from exc
    if not isinstance(value, dict):
        raise PolicyConfigurationError(f"Policy file must contain a mapping: {relative_path}")
    return value


def load_job_search_policy() -> dict[str, Any]:
    policy = _load_yaml("policy/job_search_policy.yaml")
    if not isinstance(policy.get("version"), int) or isinstance(policy.get("version"), bool) or policy["version"] < 1:
        raise PolicyConfigurationError("Job search policy requires a positive integer version")
    if not isinstance(policy.get("target_categories"), list) or not policy["target_categories"]:
        raise PolicyConfigurationError("Job search policy requires target_categories")
    if not isinstance(policy.get("employment_types"), list) or not policy["employment_types"]:
        raise PolicyConfigurationError("Job search policy requires employment_types")
    if policy.get("workplace") != "remote_only":
        raise PolicyConfigurationError("V1 workplace policy must explicitly be remote_only")
    compensation = policy.get("compensation")
    if not isinstance(compensation, dict) or not isinstance(compensation.get("accepted_types"), list):
        raise PolicyConfigurationError("Job search policy requires accepted compensation types")
    return policy


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
        domains = entry.get("domains", [])
        if not isinstance(domains, list):
            raise PolicyConfigurationError(f"Source {entry.get('id')} domains must be a list")
        if entry["enabled"] and not domains:
            raise PolicyConfigurationError(f"Enabled source {entry.get('id')} requires at least one domain")
        if any(not isinstance(domain, str) or not domain.strip() for domain in domains):
            raise PolicyConfigurationError(f"Source {entry.get('id')} contains an invalid domain")

    for entry in watchlist:
        if not isinstance(entry, dict) or not isinstance(entry.get("domain"), str):
            raise PolicyConfigurationError("Each watchlist entry requires a domain")
        if entry.get("status") not in {"blocked", "review"}:
            raise PolicyConfigurationError("Watchlist status must be blocked or review")

    return approved, watchlist
