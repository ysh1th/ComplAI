"""Summarizer Agent — LLM agent that summarizes new regulatory acts."""

import time
import logging

from models.compliance import Regulation
from models.agent_log import AgentLogEntry
from utils.llm import call_llm

logger = logging.getLogger(__name__)


async def run_summarizer_agent(
    regulation: Regulation,
) -> tuple[str, AgentLogEntry]:
    """
    Agent 5: Summarizer Agent (LLM)
    Summarizes a new regulatory act in plain language.
    """
    start = time.time()

    system_prompt = """You are a regulatory expert. Summarize regulatory acts in clear, 
concise language suitable for compliance officers. Focus on practical implications."""

    user_prompt = f"""Summarize the following new regulatory act in 3-4 clear sentences.
Focus on: what it requires, who it affects, key thresholds, and penalties for non-compliance.

Regulation:
- ID: {regulation.regulation_update_id}
- Title: {regulation.update_title}
- Summary: {regulation.summary}
- Effective date: {regulation.date_effective}

Write a plain-language summary suitable for a compliance officer. Return just the summary text, no JSON."""

    try:
        summary = await call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            json_mode=False,
            temperature=0.4,
        )
        summary = summary.strip().strip('"')

    except Exception as e:
        logger.warning(f"Summarizer LLM failed: {e}")
        summary = (
            f"{regulation.update_title}: {regulation.summary} "
            f"Effective from {regulation.date_effective}."
        )

    duration_ms = int((time.time() - start) * 1000)

    log = AgentLogEntry(
        agent="Summarizer Agent",
        icon="📝",
        status="success",
        message=f"Summarized {regulation.regulation_update_id}: {regulation.update_title}",
        duration_ms=max(duration_ms, 50),
    )

    return summary, log
