"""Run one crew agent: `uv run python -m crew.run_agent planner`."""
from __future__ import annotations

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver

from band import Agent, configure_logging
from band.adapters import LangGraphAdapter, LangGraphAdapterConfig

from crew.roles import ROLE_PROMPTS
from crew.tools import read_file, recall, remember, snyk_scan, write_file

ROLE_TOOLS = {
    "planner": [recall],
    "builder": [recall, write_file, read_file],
    "reviewer": [recall, remember, read_file],
    "sentinel": [snyk_scan, remember, recall],
}

configure_logging(logging.INFO)


def make_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=os.getenv("CREW_MODEL", "deepseek-chat"),
        base_url="https://api.deepseek.com",
        api_key=os.environ["DEEPSEEK_API_KEY"],
    )


async def main(role: str) -> None:
    load_dotenv()
    adapter = LangGraphAdapter(
        LangGraphAdapterConfig(custom_section=ROLE_PROMPTS[role]),
        llm=make_llm(),
        checkpointer=InMemorySaver(),
        additional_tools=ROLE_TOOLS[role],
    )
    async with Agent.from_config(role, adapter=adapter) as agent:
        await agent.run_forever()


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
