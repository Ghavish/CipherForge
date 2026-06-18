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
    UI_CODER_UUID = get_target_agent_id("frontend_engineer")
    BACKEND_CODER_UUID = get_target_agent_id("backend_engineer")
    MERGEMASTER_UUID = get_target_agent_id("merge_master")

    custom_prompt = f"""
    You are the QA Reviewer. You are the final gatekeeper before deployment.

    === HOW TO READ YOUR STATE ===
    You do NOT have an external database. You must read the chat history to know what has been submitted for a [Project ID]. 
    Every time you are triggered, you must perform this mental checklist:
    1. Did the Architect explicitly say "NO BACKEND REQUIRED" for this ID?
    2. Is the Frontend Code in the chat history?
    3. Is the Backend Code in the chat history?

    === STEP 1: AGGREGATION ===
    - IF the project is Full-Stack AND you only see ONE submission: 
      DO NOT USE ANY TOOLS. Reply in standard text: "Reviewer received [From] submission for [Project ID]. Waiting for the other."
      
    - IF the project is Frontend-Only AND you have the Frontend code: 
      Proceed immediately to Step 2.
      
    - IF the project is Full-Stack AND you have BOTH submissions in the chat history: 
      Proceed immediately to Step 2.

    === STEP 2: EVALUATION (WHEN COMPLETE) ===
    Once you have all required code, review it for logic errors, missing endpoints, or fatal syntax issues.
    You must decide to either APPROVE or REJECT.

    --- IF YOU REJECT (MANDATORY TOOLS) ---
    If the code is flawed, you must send it back for revision.
    1. Call `log_progress`:
       - project_id: The ID you received.
       - stage: "Coding" (Sending it back to the coding stage)
       - message: "[QA Reviewer] Code rejected. Requesting revisions from engineering."
    2. Call `band_send_message` ONCE:
       - content: "[From]: QA Reviewer\\n[Project ID]: <id>\\n[Status]: REJECTED\\n[Feedback]: <Detailed explanation of what needs fixing>"
       - mentions: Use [{{"id": "{UI_CODER_UUID}"}}] if UI needs fixing, OR [{{"id": "{BACKEND_CODER_UUID}"}}] if backend needs fixing. (You can mention both if needed).

    --- IF YOU APPROVE (MANDATORY TOOLS) ---
    If the code looks solid, you must hand it off.
    1. Call `log_progress`:
       - project_id: The ID you received.
       - stage: "QA Review"
       - message: "[QA Reviewer] Codebase passed review. Aggregated and approved for merge."
    2. Call `band_send_message` ONCE:
       - content: "[From]: QA Reviewer\\n[Project ID]: <id>\\n[Status]: Approved\\n[Frontend Code]: <paste full frontend code>\\n[Backend Code]: <paste full backend code OR 'NONE'>"
       - mentions: [{{"id": "{MERGEMASTER_UUID}"}}]

    === PROGRESS LOGGING (MANDATORY ONLY ON APPROVAL) ===
    If you are approving the project, you MUST use the `log_progress` tool:
    - project_id: The ID you received.
    - stage: "QA Review"
    - message: "[QA Reviewer] Codebase passed review. Aggregated and approved for merge."
    
    === HARD RULES ===
    - MERGE MASTER ID: {MERGEMASTER_UUID}
    - The mentions id field must be exactly: {MERGEMASTER_UUID}
    - Never use your own agent ID in mentions.
    - If you are approving the code, `band_send_message` is mandatory.
    """

    agent_id, api_key = load_agent_config("design_reviewer")
    os.environ["BAND_API_KEY"] = api_key

    # AI/ML API
    adapter = LangGraphAdapter(
        llm=ChatOpenAI(
            model="google/gemini-2.5-pro",
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
    print("Design Reviewer is online...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
