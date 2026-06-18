import os
import sys
import asyncio

from thenvoi import Agent
from thenvoi.adapters import LangGraphAdapter
from thenvoi.config import load_agent_config
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.config_parser import get_target_agent_id
from tools.db import append_log

# --- CUSTOM LOGGING TOOL ---
@tool
def log_progress(project_id: str, stage: str, message: str) -> str:
    """Use this tool to log your progress to the system UI. 
    Args:
        project_id: The ID of the current project.
        stage: The current stage (e.g., 'Coding', 'Architecture', 'QA Review').
        message: A short description of what you just completed.
    """
    append_log(project_id, stage, message)
    return "Log successfully saved to the UI."
# --------------------------------------

async def main():
    ARCHITECT_UUID = get_target_agent_id("system_architect")

    custom_prompt = f"""
    === YOUR IDENTITY ===
    You are MANAGER. You are ONLY the Manager. You do NOT write code. You do NOT review code.
    You do NOT architect systems. You do NOT act as any other agent.
    If a message is not addressed to @manager, IGNORE IT COMPLETELY and do nothing.

    === YOUR ONLY TRIGGER ===
    A message tagged "@manager NEW_BUILD_REQUEST:" containing a Project ID and task description.

    === YOUR JOB ===
    Extract the [Project ID] and the [Task]. You are the router that passes the user's raw request to the Architect.

    === PROGRESS LOGGING (MANDATORY) ===
    Before doing anything else, you MUST use the `log_progress` tool:
    - project_id: The ID you extracted.
    - stage: "Planning"
    - message: "[Manager] Task received. Initializing blueprint routing."

    === YOUR ONLY JOB ===
    When triggered, call `band_send_message` EXACTLY ONCE with:
    - content: "[From]: Manager\\n[Project ID]: <extracted project id>\\n[Task]: <extracted task>"
    - mentions: [{{"id": "SEND_TO_THIS_ID:{ARCHITECT_UUID}"}}]

    === HARD RULES ===
    - ARCHITECT ID is: {ARCHITECT_UUID}
    - The mentions id field must be EXACTLY: {ARCHITECT_UUID}
    - Do NOT use your own agent ID in mentions — ever.
    - Do NOT call band_send_message more than once per trigger.
    - After band_send_message returns success, STOP. Do nothing else.
    - Do NOT impersonate the Architect, Engineers, Reviewer, or Merge Master.
    - Do NOT write code or specs.
    """

    agent_id, api_key = load_agent_config("manager")
    os.environ["BAND_API_KEY"] = api_key

    # AI/ML API
    adapter = LangGraphAdapter(
        llm=ChatOpenAI(
            model="google/gemini-2.5-flash",
            openai_api_key=os.getenv("AIMLAPI_KEY"),
            openai_api_base="https://api.aimlapi.com"
        ),
        custom_section=custom_prompt,
        additional_tools=[log_progress]
    )

    # Featherless API
    # adapter = LangGraphAdapter(
    #     llm=ChatOpenAI(
    #         # Replace with preferred Featherless model. 
    #         model="Qwen/Qwen2.5-Coder-32B-Instruct", 
    #         openai_api_key=os.getenv("FEATHERLESS_API_KEY"),
    #         openai_api_base="https://api.featherless.ai/v1"
    #     ),
    #     custom_section=custom_prompt,
    #     additional_tools=[log_progress]
    # )

    agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)
    print("Manager is online and awaiting user requests...")
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())