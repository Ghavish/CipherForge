import os
import sys
import asyncio
import json
from datetime import datetime

from thenvoi import Agent
from thenvoi.adapters import LangGraphAdapter
from thenvoi.config import load_agent_config
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.config_parser import get_target_agent_id
from tools.db import append_log

# --- Memory tracking ---
REVIEW_MEMORY = {}  # project_id -> {review_count, last_review_time, issues_found, status}

@tool
def log_progress(project_id: str, stage: str, message: str) -> str:
    """Use this tool to log your progress to the system UI."""
    append_log(project_id, stage, message)
    return "Log successfully saved to the UI."

# --- Memory management tool ---
REVIEW_STATE = {}

def get_review_state(project_id: str) -> str:
    """
    Get the current review state for a project to prevent duplicate reviews.
    Returns JSON with: {review_count, status, last_issue, last_review_time}
    """
    if project_id not in REVIEW_STATE:
        REVIEW_STATE[project_id] = {
            "review_count": 0,
            "status": "new",
            "last_issue": None,
            "last_review_time": None,
            "reviewed_code_hash": None
        }
    return json.dumps(REVIEW_STATE[project_id])

@tool
def update_review_state(project_id: str, status: str, issue: str = "", code_hash: str = "") -> str:
    """
    Update the review state after reviewing code.
    """
    if project_id not in REVIEW_STATE:
        REVIEW_STATE[project_id] = {"review_count": 0}
    
    REVIEW_STATE[project_id]["review_count"] += 1
    REVIEW_STATE[project_id]["status"] = status
    REVIEW_STATE[project_id]["last_issue"] = issue
    REVIEW_STATE[project_id]["last_review_time"] = datetime.now().isoformat()
    if code_hash:
        REVIEW_STATE[project_id]["reviewed_code_hash"] = code_hash
    return f"Review state updated: {status} (count: {REVIEW_STATE[project_id]['review_count']})"

@tool
def should_auto_approve(project_id: str) -> str:
    """
    Check if a project has been reviewed too many times and should auto-approve.
    Returns "AUTO_APPROVE" if review_count >= 3, otherwise "CONTINUE".
    """
    if project_id not in REVIEW_STATE:
        REVIEW_STATE[project_id] = {"review_count": 0}
    
    review_count = REVIEW_STATE[project_id]["review_count"]
    if review_count >= 3:
        return f"AUTO_APPROVE: Project has been reviewed {review_count} times. Auto-approving to prevent infinite loop."
    return f"CONTINUE: Review {review_count + 1} of 3."

# --- LOGGING TOOL ---
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

async def main():
    UI_CODER_UUID = get_target_agent_id("frontend_engineer")
    BACKEND_CODER_UUID = get_target_agent_id("backend_engineer")
    MERGEMASTER_UUID = get_target_agent_id("merge_master")

    custom_prompt = f"""
    You are the QA Reviewer. You are the final gatekeeper before deployment.

    === TOOL AVAILABILITY ===
    You have these tools available:
    1. get_review_state(project_id) - Check review history
    2. update_review_state(project_id, status, issue) - Update review status
    3. should_auto_approve(project_id) to check if you should auto-approve.
    3. log_progress(project_id, stage, message) - Log progress
    4. band_send_message(content, mentions) - Send messages

    If `should_auto_approve` returns "AUTO_APPROVE", you MUST:
    - Skip all review logic
    - Call `update_review_state` with status="auto_approved"
    - Call `log_progress` with message "[QA Reviewer] Auto-approved after 3+ review cycles"
    - Call `band_send_message` to send to Merge Master with the code
    - STOP

    === MEMORY SYSTEM ===
    You now have a memory system to prevent infinite review loops:
    1. ALWAYS call `get_review_state` first to check if you've already reviewed this project
    2. If review_count >= 2 AND the same code is submitted, AUTO-APPROVE and proceed
    3. Track what issues you've already raised

    === HOW TO READ YOUR STATE ===
    You do NOT have an external database. You must:
    1. First call `get_review_state` to check review history
    2. Then read the chat history to know what has been submitted

    === REVIEW COUNT LOGIC (CRITICAL) ===
    - review_count = 0: First review. Do thorough analysis.
    - review_count = 1: Second review. Check only if fixes were applied.
    - review_count >= 2: AUTO-APPROVE. The team has tried enough.

    === STEP 1: CHECK HISTORY ===
    ALWAYS start by calling `get_review_state(project_id)` to see:
    - How many times you've reviewed this project
    - What issues you raised last time
    - The current status

    === STEP 2: AGGREGATION ===
    - IF the project is Full-Stack AND you only see ONE submission: 
      Reply: "Reviewer received [From] submission for [Project ID]. Waiting for the other."
      
    - IF the project is Frontend-Only AND you have the Frontend code: 
      Proceed to Step 3.
      
    - IF the project is Full-Stack AND you have BOTH submissions: 
      Proceed to Step 3.

    === STEP 3: REVIEW LOGIC ===
    If review_count >= 2:
        - AUTO-APPROVE immediately with note: "Auto-approved after multiple review cycles"
        - Auto-approve to prevent loops.
    
    If review_count == 1:
        - Only check if previous issues were fixed
        - If fixed: APPROVE
        - If not fixed: REJECT with reminder of previous feedback
    
    If review_count == 0:
        - Do full review
        - Check for critical security issues (eval(), XSS, SQL injection)
        - Check for logic errors
        - Check for missing features

    === IF YOU REJECT ===
    1. Call `update_review_state`: status="rejected", issue="<brief description>"
    2. Call `log_progress`: stage="Coding", message="[QA Reviewer] Code rejected. Requesting revisions."
    3. Call `band_send_message`:
       - content: "[From]: QA Reviewer\\n[Project ID]: <id>\\n[Status]: REJECTED\\n[Feedback]: <specific fixes needed>"
       - mentions: [{{"id": "{UI_CODER_UUID}"}}] or [{{"id": "{BACKEND_CODER_UUID}"}}]

    === IF YOU APPROVE ===
    1. Call `update_review_state`: status="approved"
    2. Call `log_progress`: stage="QA Review", message="[QA Reviewer] Codebase passed review. Approved for merge."
    3. Call `band_send_message`:
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
    - If review_count >= 2, you MUST auto-approve to prevent loops.
    - ALWAYS call `get_review_state` first before doing anything else.
    - If you are approving the code, `band_send_message` is mandatory.
    """

    agent_id, api_key = load_agent_config("design_reviewer")
    os.environ["BAND_API_KEY"] = api_key

    # AI/ML API
    adapter = LangGraphAdapter(
        llm=ChatOpenAI(
            model="claude-opus-4-8",
            openai_api_key=os.getenv("AIMLAPI_KEY"),
            openai_api_base="https://api.aimlapi.com"
        ),
        custom_section=custom_prompt,
        additional_tools=[log_progress, get_review_state, update_review_state, should_auto_approve]
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
