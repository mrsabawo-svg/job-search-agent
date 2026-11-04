from pathlib import Path, PurePosixPath
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
    if policy.get("status") not in {"draft", "approved", "retired"}:
        raise PolicyConfigurationError("Job search policy status must be draft, approved or retired")
    if policy["status"] == "approved":
        approval = policy.get("approval")
        required_approval_fields = ("approved_on", "basis", "scope", "constraints")
        if not isinstance(approval, dict) or any(
            field not in approval for field in required_approval_fields
        ):
            raise PolicyConfigurationError("Approved policy requires a complete approval record")
        if not isinstance(approval["approved_on"], str) or not approval["approved_on"].strip():
            raise PolicyConfigurationError("Approved policy requires an approval date")
        if any(
            not isinstance(approval[field], str) or not approval[field].strip()
            for field in ("basis", "scope")
        ):
            raise PolicyConfigurationError("Approved policy requires approval basis and scope")
        if not isinstance(approval["constraints"], list) or not approval["constraints"] or any(
            not isinstance(item, str) or not item.strip() for item in approval["constraints"]
        ):
            raise PolicyConfigurationError("Approved policy requires non-empty approval constraints")
    if not isinstance(policy.get("version"), int) or isinstance(policy.get("version"), bool) or policy["version"] < 1:
        raise PolicyConfigurationError("Job search policy requires a positive integer version")
    if not isinstance(policy.get("target_categories"), list) or not policy["target_categories"]:
        raise PolicyConfigurationError("Job search policy requires target_categories")
    if not isinstance(policy.get("employment_types"), list) or not policy["employment_types"]:
        raise PolicyConfigurationError("Job search policy requires employment_types")
    if policy.get("workplace") != "remote_only":
        raise PolicyConfigurationError("V1 workplace policy must explicitly be remote_only")

    compensation = policy.get("compensation")
    if not isinstance(compensation, dict):
        raise PolicyConfigurationError("Job search policy requires compensation settings")
    accepted_types = compensation.get("accepted_types")
    if not isinstance(accepted_types, list) or not accepted_types:
        raise PolicyConfigurationError("Job search policy requires accepted compensation types")
    for setting in ("require_amount", "require_currency", "require_period", "reject_unspecified"):
        if not isinstance(compensation.get(setting), bool):
            raise PolicyConfigurationError(f"Compensation policy requires boolean setting: {setting}")
    if any(not isinstance(value, str) or not value for value in accepted_types):
        raise PolicyConfigurationError("Accepted compensation types must be non-empty strings")

    geography = policy.get("geography")
    if not isinstance(geography, dict):
        raise PolicyConfigurationError("Job search policy requires geography settings")
    if not isinstance(geography.get("require_country_or_region_statement"), bool):
        raise PolicyConfigurationError("Geography policy requires require_country_or_region_statement boolean")
    for setting in ("unknown_eligibility", "applicant_location_match_without_profile"):
        if geography.get(setting) not in {"REVIEW", "REJECT"}:
            raise PolicyConfigurationError(f"Geography policy requires {setting} to be REVIEW or REJECT")

    employer = policy.get("employer")
    if not isinstance(employer, dict):
        raise PolicyConfigurationError("Job search policy requires employer settings")
    for setting in ("require_verifiable_identity", "require_official_domain_or_approved_ats"):
        if not isinstance(employer.get(setting), bool):
            raise PolicyConfigurationError(f"Employer policy requires {setting} boolean")
    if employer.get("identity_relationship_unverified") not in {"REVIEW", "REJECT"}:
        raise PolicyConfigurationError("Employer policy requires identity_relationship_unverified to be REVIEW or REJECT")

    role = policy.get("role")
    if not isinstance(role, dict):
        raise PolicyConfigurationError("Job search policy requires role settings")
    if role.get("require_target_category_match") is not True:
        raise PolicyConfigurationError("V1 role policy must require target category matching")
    if role.get("unrelated_roles") != "REJECT":
        raise PolicyConfigurationError("V1 unrelated-role policy must be REJECT")

    if any(not isinstance(item, str) or not item.strip() for item in policy["target_categories"]):
        raise PolicyConfigurationError("Target categories must be non-empty strings")
    if len(policy["target_categories"]) != len(set(policy["target_categories"])):
        raise PolicyConfigurationError("Target categories must be unique")
    if any(not isinstance(item, str) or not item.strip() for item in policy["employment_types"]):
        raise PolicyConfigurationError("Employment types must be non-empty strings")
    if len(policy["employment_types"]) != len(set(policy["employment_types"])):
        raise PolicyConfigurationError("Employment types must be unique")

    sources = policy.get("sources")
    if not isinstance(sources, dict):
        raise PolicyConfigurationError("Job search policy requires source settings")
    if not isinstance(sources.get("employer_ats_only_by_default"), bool):
        raise PolicyConfigurationError("Source policy requires employer_ats_only_by_default boolean")
    for setting in ("approved_source_file", "watchlist_file"):
        if not isinstance(sources.get(setting), str) or not sources[setting]:
            raise PolicyConfigurationError(f"Source policy requires {setting}")
    return policy


def _policy_relative_path(value: str, setting: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise PolicyConfigurationError(f"Source policy {setting} must be a safe repository-relative path")
    return str(path)


def load_source_policy() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    source_settings = load_job_search_policy()["sources"]
    approved_path = _policy_relative_path(source_settings["approved_source_file"], "approved_source_file")
    watchlist_path = _policy_relative_path(source_settings["watchlist_file"], "watchlist_file")
    approved_data = _load_yaml(approved_path)
    watchlist_data = _load_yaml(watchlist_path)
    approved = approved_data.get("approved_sources")
    watchlist = watchlist_data.get("watchlist")
    if not isinstance(approved, list) or not isinstance(watchlist, list):
        raise PolicyConfigurationError("Source policy requires approved_sources and watchlist lists")

    seen_ids = set()
    for entry in approved:
        if not isinstance(entry, dict) or not isinstance(entry.get("id"), str) or not entry["id"].strip():
            raise PolicyConfigurationError("Each approved source requires a non-empty id")
        source_id = entry["id"]
        if source_id in seen_ids:
            raise PolicyConfigurationError(f"Duplicate approved source id: {source_id}")
        seen_ids.add(source_id)
        if entry.get("type") not in {"employer_ats", "job_board"}:
            raise PolicyConfigurationError(f"Source {source_id} has an invalid type")
        if not isinstance(entry.get("enabled"), bool):
            raise PolicyConfigurationError(f"Source {source_id} requires an enabled boolean")
        if entry["type"] == "job_board" and not isinstance(entry.get("explicit_approval"), bool):
            raise PolicyConfigurationError(f"Job board {source_id} requires an explicit_approval boolean")
        domains = entry.get("domains", [])
        if not isinstance(domains, list):
            raise PolicyConfigurationError(f"Source {source_id} domains must be a list")
        if entry["enabled"] and not domains:
            raise PolicyConfigurationError(f"Enabled source {source_id} requires at least one domain")
        if any(not isinstance(domain, str) or not domain.strip() for domain in domains):
            raise PolicyConfigurationError(f"Source {source_id} contains an invalid domain")

    for entry in watchlist:
        if not isinstance(entry, dict) or not isinstance(entry.get("domain"), str):
            raise PolicyConfigurationError("Each watchlist entry requires a domain")
        if entry.get("status") not in {"blocked", "review"}:
            raise PolicyConfigurationError("Watchlist status must be blocked or review")

    return approved, watchlist

def load_decision_catalogue() -> dict[str, dict[str, str]]:
    """Load and validate the policy-authorized rejection and review codes."""
    policy = load_job_search_policy()
    catalogue = _load_yaml("policy/rejection_reasons.yaml")
    rejection_reasons = catalogue.get("rejection_reasons")
    review_flags = catalogue.get("review_flags")
    if not isinstance(rejection_reasons, dict) or not isinstance(review_flags, dict):
        raise PolicyConfigurationError(
            "Decision catalogue requires rejection_reasons and review_flags mappings"
        )

    for group_name, entries in (
        ("rejection_reasons", rejection_reasons),
        ("review_flags", review_flags),
    ):
        for code, description in entries.items():
            if not isinstance(code, str) or not code.strip():
                raise PolicyConfigurationError(f"{group_name} contains an invalid code")
            if not isinstance(description, str) or not description.strip():
                raise PolicyConfigurationError(f"Decision code {code} requires a description")

    hard_rejections = policy.get("hard_rejections")
    human_review_required = policy.get("human_review_required")
    for setting, codes in (
        ("hard_rejections", hard_rejections),
        ("human_review_required", human_review_required),
    ):
        if not isinstance(codes, list) or any(
            not isinstance(code, str) or not code.strip() for code in codes
        ):
            raise PolicyConfigurationError(f"Policy requires a valid {setting} list")
        if len(codes) != len(set(codes)):
            raise PolicyConfigurationError(f"Policy {setting} contains duplicate codes")

    hard_set = set(hard_rejections)
    review_set = set(human_review_required)
    if hard_set & review_set:
        raise PolicyConfigurationError("A decision code cannot be both rejection and review")
    if not hard_set <= set(rejection_reasons):
        raise PolicyConfigurationError("Hard rejection policy references undocumented codes")
    if not review_set <= set(review_flags):
        raise PolicyConfigurationError("Human review policy references undocumented flags")

    return {
        "rejection_reasons": rejection_reasons,
        "review_flags": review_flags,
    }


def validate_decision_codes(reason_codes: list[str], review_flags: list[str]) -> None:
    """Reject runtime findings that are not explicitly authorized by policy."""
    policy = load_job_search_policy()
    catalogue = load_decision_catalogue()
    hard_rejections = set(policy["hard_rejections"])
    human_review_required = set(policy["human_review_required"])

    unknown_reasons = set(reason_codes) - hard_rejections
    unknown_flags = set(review_flags) - human_review_required
    if unknown_reasons:
        raise PolicyConfigurationError(
            f"Runtime emitted rejection codes not authorized by policy: {sorted(unknown_reasons)}"
        )
    if unknown_flags:
        raise PolicyConfigurationError(
            f"Runtime emitted review flags not authorized by policy: {sorted(unknown_flags)}"
        )
    if set(reason_codes) - set(catalogue["rejection_reasons"]):
        raise PolicyConfigurationError("Runtime emitted undocumented rejection codes")
    if set(review_flags) - set(catalogue["review_flags"]):
        raise PolicyConfigurationError("Runtime emitted undocumented review flags")

