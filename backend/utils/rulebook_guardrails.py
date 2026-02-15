import logging
from models.compliance import Rulebook

logger = logging.getLogger(__name__)

REQUIRED_TOP_LEVEL_KEYS = {
    "amount_based",
    "frequency_based",
    "location_based",
    "behavioural_pattern",
    "risk_score",
    "risk_bands",
}

VALID_JURISDICTIONS = {"MT", "AE", "KY"}

POINT_MIN = 0
POINT_MAX = 50

RISK_SCORE_RANGE = {"range": "0-100"}

REQUIRED_RISK_BANDS = {"HIGH", "MEDIUM", "LOW", "CLEAN"}

RULEBOOK_TEMPLATE = {
    "amount_based": list,
    "frequency_based": list,
    "location_based": list,
    "behavioural_pattern": list,
    "risk_score": dict,
    "risk_bands": dict,
}


def validate_rulebook_structure(rulebook_data: dict) -> list[str]:
    errors = []
    for key, expected_type in RULEBOOK_TEMPLATE.items():
        if key not in rulebook_data:
            errors.append(f"Missing required key: '{key}'")
        elif not isinstance(rulebook_data[key], expected_type):
            errors.append(
                f"Key '{key}' expected {expected_type.__name__}, "
                f"got {type(rulebook_data[key]).__name__}"
            )

    risk_score = rulebook_data.get("risk_score", {})
    if isinstance(risk_score, dict):
        if "rules" not in risk_score:
            errors.append("risk_score missing 'rules' list")
        if "capping" not in risk_score:
            errors.append("risk_score missing 'capping' field")

    risk_bands = rulebook_data.get("risk_bands", {})
    if isinstance(risk_bands, dict):
        missing = REQUIRED_RISK_BANDS - set(risk_bands.keys())
        if missing:
            errors.append(f"risk_bands missing keys: {missing}")

    return errors


def validate_point_bounds(rulebook_data: dict) -> tuple[dict, list[str]]:
    warnings = []
    risk_score = rulebook_data.get("risk_score", {})
    rules = risk_score.get("rules", [])

    clamped_rules = []
    for rule in rules:
        if isinstance(rule, dict) and "points" in rule:
            points = rule["points"]
            if isinstance(points, (int, float)):
                if points < POINT_MIN:
                    warnings.append(
                        f"Rule '{rule.get('rule', '?')}' had points={points}, clamped to {POINT_MIN}"
                    )
                    rule["points"] = POINT_MIN
                elif points > POINT_MAX:
                    warnings.append(
                        f"Rule '{rule.get('rule', '?')}' had points={points}, clamped to {POINT_MAX}"
                    )
                    rule["points"] = POINT_MAX
        clamped_rules.append(rule)

    rulebook_data["risk_score"]["rules"] = clamped_rules
    return rulebook_data, warnings


def validate_jurisdiction(rulebook_data: dict, expected_jurisdiction: str) -> list[str]:
    errors = []
    if expected_jurisdiction.upper() not in VALID_JURISDICTIONS:
        errors.append(
            f"Invalid jurisdiction '{expected_jurisdiction}'. "
            f"Must be one of {VALID_JURISDICTIONS}"
        )

    for key in ["amount_based", "frequency_based", "location_based", "behavioural_pattern"]:
        rules = rulebook_data.get(key, [])
        for rule_text in rules:
            if isinstance(rule_text, str):
                for jc in VALID_JURISDICTIONS:
                    if jc != expected_jurisdiction.upper():
                        jurisdiction_names = {"MT": "Malta", "AE": "UAE", "KY": "Cayman"}
                        name = jurisdiction_names.get(jc, jc)
                        if name.lower() in rule_text.lower() and expected_jurisdiction.upper() != jc:
                            pass

    return errors


def apply_guardrails(
    rulebook_data: dict,
    jurisdiction_code: str,
    previous_rulebook: Rulebook | None = None,
) -> tuple[dict, list[str]]:
    all_issues = []

    structural_errors = validate_rulebook_structure(rulebook_data)
    if structural_errors:
        all_issues.extend([f"[STRUCTURE] {e}" for e in structural_errors])
        if previous_rulebook:
            logger.warning(
                f"Rulebook failed structural validation, restoring from previous: {structural_errors}"
            )
            rulebook_data = previous_rulebook.model_dump()
            return rulebook_data, all_issues

    rulebook_data, point_warnings = validate_point_bounds(rulebook_data)
    all_issues.extend([f"[BOUNDS] {w}" for w in point_warnings])

    jurisdiction_errors = validate_jurisdiction(rulebook_data, jurisdiction_code)
    all_issues.extend([f"[JURISDICTION] {e}" for e in jurisdiction_errors])

    for key in ["amount_based", "frequency_based", "location_based", "behavioural_pattern"]:
        if key not in rulebook_data or not isinstance(rulebook_data[key], list):
            if previous_rulebook:
                rulebook_data[key] = getattr(previous_rulebook, key, [])
                all_issues.append(f"[RESTORE] Restored '{key}' from previous rulebook")

    return rulebook_data, all_issues
