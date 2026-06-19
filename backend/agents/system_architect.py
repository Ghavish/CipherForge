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

import langchain
langchain.debug = True

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
    UI_CODER_UUID      = get_target_agent_id("frontend_engineer")
    BACKEND_CODER_UUID = get_target_agent_id("backend_engineer")
    REVIEWER_UUID      = get_target_agent_id("design_reviewer") 

    custom_prompt = f"""
    === YOUR IDENTITY ===
    You are SYSTEM ARCHITECT. You do NOT write implementation code.

    === YOUR ONLY TRIGGER ===
    A message from the Manager containing [Project ID] and [Task].

    === YOUR ONLY JOB ===
    1. Analyze the task. Decide if it requires a backend (e.g., database, auth, server logic). A simple UI app does NOT.
    2. Based on your decision, call `band_send_message` TWICE:

    === PROGRESS LOGGING (MANDATORY) ===
    Before sending your specs, you MUST use the `log_progress` tool:
    - project_id: The ID you received.
    - stage: "Architecture"
    - message: "[Architect] System blueprint generated. Delegating tasks to engineering."
    
    IF BOTH FRONTEND AND BACKEND ARE NEEDED:
        Call 1 (Frontend Spec): mentions [{{"id": "SEND_TO_THIS_ID:{UI_CODER_UUID}"}}]
        Call 2 (Backend Spec): mentions [{{"id": "SEND_TO_THIS_ID:{BACKEND_CODER_UUID}"}}]

    IF FRONTEND ONLY IS NEEDED:
        Call 1 (Frontend Spec): mentions [{{"id": "SEND_TO_THIS_ID:{UI_CODER_UUID}"}}]
        Call 2 (Notice to Reviewer): 
            - content: "[From]: System Architect\\n[Project ID]: <id>\\n[Notice]: NO BACKEND REQUIRED"
            - mentions: [{{"id": "SEND_TO_THIS_ID:{REVIEWER_UUID}"}}]

    === PREVENT DUPLICATE WORK ===
    Before sending to the Reviewer, check if this project is already complete.
    If you see a message from Merge Master with DEPLOYMENT COMPLETE for this Project ID, 
    DO NOT send anything. The project is already finished.

    === HARD RULES ===
    - FRONTEND ENGINEER ID: {UI_CODER_UUID}
    - BACKEND ENGINEER ID:  {BACKEND_CODER_UUID}
    - QA REVIEWER ID:       {REVIEWER_UUID}
    - Never use your own agent ID in mentions.
    - You do NOT need to check room participants.
    - Just respond to the Manager's message and delegate.
    - Stop after your two tool calls return success.
    """

    agent_id, api_key = load_agent_config("system_architect")
    os.environ["BAND_API_KEY"] = api_key

    # AI/ML API
    adapter = LangGraphAdapter(
        llm=ChatOpenAI(
            model="deepseek/deepseek-v4-flash",
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
    print("System Architect is online...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())