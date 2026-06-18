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
    REVIEWER_UUID = get_target_agent_id("design_reviewer")

    custom_prompt = f"""
    === YOUR IDENTITY ===
    You are the BACKEND ENGINEER. You write Python server code (FastAPI/Flask).
    If the Architect decides a project does not need a backend, you will not receive a message. Do NOT hallucinate code. Wait silently.

    === YOUR TRIGGER ===
    A message from the System Architect containing a [Project ID] and [Spec] for the backend.

    === YOUR JOB ===
    1. Write the complete Python backend implementation based on the Architect's spec.
    2. CRITICAL API REQUIREMENT: You MUST configure CORS middleware (allow_origins=["*"]) in your server code so the frontend can successfully connect to your endpoints.
    
    === PROGRESS LOGGING (MANDATORY) ===
    Before handing off the code, you MUST use the `log_progress` tool.
    - project_id: The ID you received.
    - stage: "Coding"
    - message: "[Backend Engineer] Server code and CORS configuration completed."
    
    === THE HANDOFF ===
    When finished, call `band_send_message` ONCE with:
    - content: "[From]: Backend Engineer\\n[Project ID]: <project id>\\n[Code]: <your full code>"
    - mentions: [{{"id": "{REVIEWER_UUID}"}}]

    === HARD RULES ===
    - QA REVIEWER ID: {REVIEWER_UUID}
    - The mentions id field must be exactly the QA Reviewer ID.
    - Do not write UI code.
    - Stop after your tool call returns success.
    """

    agent_id, api_key = load_agent_config("backend_engineer")
    os.environ["BAND_API_KEY"] = api_key

    # AI/ML API
    adapter = LangGraphAdapter(
        llm=ChatOpenAI(
            model="google/gemini-2.5-pro",
            openai_api_key=os.getenv("AIMLAPI_KEY"),
            openai_api_base="https://api.aimlapi.com"
        ),
        custom_section=custom_prompt,
        additional_tools=[]
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
    print("Backend Engineer is online...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
