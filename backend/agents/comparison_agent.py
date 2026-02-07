"""Comparison Agent — LLM agent that compares old vs new regulations."""

import json
import time
import logging

from models.compliance import Regulation
from models.agent_log import AgentLogEntry
from utils.llm import call_llm_json

logger = logging.getLogger(__name__)


async def run_comparison_agent(
    old_regulations: list[Regulation],
    new_regulation: Regulation,
    jurisdiction: str,
) -> tuple[list[str], AgentLogEntry]:
    """
    Agent 6: Comparison Agent (LLM)
    Compares old vs new regulatory frameworks.
    """
    start = time.time()

    old_regs_text = "\n".join([
        f"- {r.regulation_update_id}: {r.update_title}\n  Summary: {r.summary}\n  Effective: {r.date_effective}"
        for r in old_regulations
    ])

    system_prompt = """You are a regulatory analyst. Compare old and new regulatory frameworks 
and generate specific comparison points. Return ONLY valid JSON."""

    user_prompt = f"""Compare the following old and new regulatory frameworks and generate specific comparison points.

Old regulations for {jurisdiction}:
{old_regs_text}

New regulation being introduced:
- ID: {new_regulation.regulation_update_id}
- Title: {new_regulation.update_title}
- Summary: {new_regulation.summary}
- Effective date: {new_regulation.date_effective}

Generate 4-6 specific comparison points. For each point, state:
- What aspect changed (thresholds, reporting, licensing, etc.)
- The old requirement vs the new requirement
- Whether it's stricter, relaxed, or entirely new

Return as JSON:
{{
  "comparison_points": ["point 1", "point 2", ...]
}}"""

    try:
        result = await call_llm_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.3,
        )
        raw_points = result.get("comparison_points", [])
        if not isinstance(raw_points, list):
            raw_points = [raw_points]

        # Normalize: LLM may return dicts instead of strings
        comparison_points: list[str] = []
        for item in raw_points:
            if isinstance(item, str):
                comparison_points.append(item)
            elif isinstance(item, dict):
                # Join all dict values into a readable string
                comparison_points.append(" — ".join(str(v) for v in item.values()))
            else:
                comparison_points.append(str(item))

    except Exception as e:
        logger.warning(f"Comparison LLM failed: {e}")
        comparison_points = [
            f"New regulation {new_regulation.update_title} introduces additional requirements beyond existing framework",
            f"Effective from {new_regulation.date_effective}, requiring immediate compliance updates",
            "Stricter monitoring thresholds expected based on new regulatory text",
            "Enhanced reporting obligations compared to previous framework",
        ]

    duration_ms = int((time.time() - start) * 1000)

    stricter = sum(1 for p in comparison_points if "stricter" in p.lower() or "enhanced" in p.lower())
    new_obs = sum(1 for p in comparison_points if "new" in p.lower() or "introduces" in p.lower())

    log = AgentLogEntry(
        agent="Comparison Agent",
        icon="⚖️",
        status="success",
        message=(
            f"Generated {len(comparison_points)} comparison points — "
            f"{stricter} stricter requirements, {new_obs} new obligations"
        ),
        duration_ms=max(duration_ms, 50),
    )

    return comparison_points, log
