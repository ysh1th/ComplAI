import os
import json
import logging
import asyncio
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv
from google import genai

load_dotenv()

logger = logging.getLogger(__name__)

client = genai.Client(api_key=os.getenv("LLM_API_KEY"))

MODEL = os.getenv("LLM_MODEL", "gemini-2.0-flash")

MAX_RETRIES = 3

T = TypeVar("T", bound=BaseModel)


async def call_llm(
    system_prompt: str,
    user_prompt: str,
    json_mode: bool = True,
    temperature: float = 0.3,
) -> str:
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


async def call_llm_json(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.3,
) -> dict:
    content = await call_llm(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        json_mode=True,
        temperature=temperature,
    )
    return json.loads(content)


async def call_llm_validated(
    system_prompt: str,
    user_prompt: str,
    response_model: Type[T],
    temperature: float = 0.3,
    max_retries: int = MAX_RETRIES,
) -> tuple[T, int]:
    """
    Call LLM with Pydantic validation retry loop.

    On each attempt:
      1. Call the LLM for JSON output.
      2. Parse and validate against `response_model`.
      3. If ValidationError, retry with error feedback in the prompt.

    Returns (validated_model, retry_count).
    Raises the last exception after all retries are exhausted.
    """
    last_error: Exception | None = None
    current_prompt = user_prompt

    for attempt in range(1, max_retries + 1):
        try:
            raw = await call_llm(
                system_prompt=system_prompt,
                user_prompt=current_prompt,
                json_mode=True,
                temperature=temperature,
            )

            data = json.loads(raw)
            validated = response_model.model_validate(data)
            return validated, attempt - 1

        except (ValidationError, json.JSONDecodeError) as e:
            last_error = e
            error_msg = str(e)
            logger.warning(
                f"LLM output validation failed (attempt {attempt}/{max_retries}): {error_msg[:200]}"
            )

            current_prompt = (
                f"{user_prompt}\n\n"
                f"--- CORRECTION REQUIRED (attempt {attempt + 1}) ---\n"
                f"Your previous response failed validation with this error:\n"
                f"{error_msg}\n\n"
                f"Please fix the JSON output to match the required schema exactly. "
                f"Return ONLY valid JSON."
            )

        except Exception as e:
            last_error = e
            logger.error(f"LLM call failed on attempt {attempt}: {e}")
            if attempt == max_retries:
                break

    raise last_error or RuntimeError("LLM call exhausted all retries")
