"""LLM client wrapper for all agent calls — uses Google GenAI SDK."""

import os
import json
import logging
import asyncio
from dotenv import load_dotenv
from google import genai

load_dotenv()

logger = logging.getLogger(__name__)

client = genai.Client(api_key=os.getenv("LLM_API_KEY"))

MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")


async def call_llm(
    system_prompt: str,
    user_prompt: str,
    json_mode: bool = True,
    temperature: float = 0.3,
) -> str:
    """
    Wrapper for LLM calls used by all agents.

    Returns the raw response content string.
    Raises exception on failure (agents should handle fallbacks).
    """
    try:
        config = {
            "temperature": temperature,
            "system_instruction": system_prompt,
        }
        if json_mode:
            config["response_mime_type"] = "application/json"

        response = await asyncio.to_thread(
            client.models.generate_content,
            model=MODEL,
            contents=user_prompt,
            config=config,
        )

        content = response.text
        if content is None:
            raise ValueError("LLM returned empty content")

        return content

    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise


async def call_llm_json(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
) -> dict:
    """Call LLM and parse the response as JSON."""
    content = await call_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        json_mode=True,
        temperature=temperature,
    )
    return json.loads(content)
