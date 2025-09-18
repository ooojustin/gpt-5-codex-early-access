from __future__ import annotations

import os
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.responses import ResponseStreamEvent

PROMPT_TEXT = (
    "What model are you, and what application are you currently being used inside of?"
)

INSTRUCTIONS_FILE = Path(__file__).parent / "prompts" / "instructions.txt"
SYSTEM_PROMPT_FILE = Path(__file__).parent / "prompts" / "system.txt"


def build_openai_client(api_key: str) -> OpenAI:
    allow_insecure = os.getenv("OPENAI_ALLOW_INSECURE_SSL") == "1"

    client_kwargs: dict[str, Any] = {"api_key": api_key}

    base_url = os.getenv("OPENAI_BASE_URL")
    if base_url:
        client_kwargs["base_url"] = base_url

    if allow_insecure:
        client_kwargs["http_client"] = httpx.Client(verify=False)

    return OpenAI(**client_kwargs)


def load_instructions() -> str | None:
    if not INSTRUCTIONS_FILE.is_file():
        return None

    instructions = INSTRUCTIONS_FILE.read_text().strip()
    return instructions or None


def load_system_prompt() -> str | None:
    if not SYSTEM_PROMPT_FILE.is_file():
        return None

    instructions = SYSTEM_PROMPT_FILE.read_text().strip()
    return instructions or None


def stream_response_text(events: Iterable[ResponseStreamEvent]) -> None:
    for event in events:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
        elif event.type == "response.completed":
            print(flush=True)


def main() -> None:
    load_dotenv(dotenv_path=".env", override=False)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        sys.stderr.write("Missing OPENAI_API_KEY environment variable.\n")
        sys.exit(1)

    model = os.getenv("OPENAI_MODEL", "gpt-5")

    client = build_openai_client(api_key)
    instructions = load_instructions()
    sys_prompt = load_system_prompt()

    input_messages = [
        {
            "role": "system",
            "content": sys_prompt,
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": PROMPT_TEXT,
                }
            ],
        },
    ]

    # NOTES:
    # - 'store' must be set to false
    # - 'input' must be in list format
    # - 'model' can only be gpt-5 or gpt-5-codex
    # - 'instructions' need to match codex (see prompts/instructions.txt)
    stream_kwargs: dict[str, Any] = {
        "model": model,
        "input": input_messages,
        "store": False,
    }
    if instructions:
        stream_kwargs["instructions"] = instructions

    with client.responses.stream(**stream_kwargs) as stream:
        stream_response_text(stream)
        stream.get_final_response()


if __name__ == "__main__":
    main()
