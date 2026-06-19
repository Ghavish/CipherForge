import os
import sys
import asyncio
import re
import requests
import json

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

# ---------- CUSTOM TOOLS ----------
@tool(description="Log progress to the system UI.")
def log_progress(project_id: str, stage: str, message: str) -> str:
    """Log progress to the system UI."""
    append_log(project_id, stage, message)
    return "Log successfully saved to the UI."

@tool(description="Create a new room and add all participants. Returns ROOM_ID: <uuid> | ...")
def create_room_and_add_all_participants(
    project_id: str,
    manager_id: str,
    architect_id: str,
    ui_coder_id: str,
    backend_coder_id: str,
    reviewer_id: str,
    merge_master_id: str
) -> str:
    base_url = os.getenv("BAND_REST_URL", "https://app.band.ai/")
    if not base_url.endswith("/"):
        base_url += "/"

    api_base = f"{base_url}api/v1/agent"
    create_url = f"{api_base}/chats"
    participants_url_template = f"{api_base}/chats/{{room_id}}/participants"

    api_key = os.getenv("BAND_API_KEY")
    if not api_key:
        return "ERROR: BAND_API_KEY environment variable is not set."

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }

    room_name = f"{project_id}-WAR-ROOM"

    # 1. CREATE THE ROOM
    try:
        create_resp = requests.post(
            create_url,
            headers=headers,
            json={"chat": {}}, 
            timeout=10
        )
    except Exception as e:
        return f"ERROR: Failed to connect to Band API – {str(e)}"

    if create_resp.status_code != 201:
        return f"ERROR: Could not create room – {create_resp.status_code} {create_resp.text}"

    room_data = create_resp.json()
    room_id = room_data.get("data", {}).get("id")
    if not room_id:
        return f"ERROR: No room ID in response: {room_data}"

    # 2. ADD PARTICIPANTS (Using the exact nested schema!)
    participants = [
        # ("Manager", manager_id),
        ("Architect", architect_id),
        ("Frontend Engineer", ui_coder_id),
        ("Backend Engineer", backend_coder_id),
        ("QA Reviewer", reviewer_id),
        ("Merge Master", merge_master_id)
    ]

    added = []
    failed = []

    # Using a Session prevents the HTTPSConnectionPool from exhausting and timing out
    with requests.Session() as session:
        session.headers.update(headers)

        for name, agent_id in participants:
            try:
                add_url = participants_url_template.format(room_id=room_id)
                
                # The exact schema required by the Band REST API
                payload = {
                    "participant": {
                        "participant_id": agent_id
                    }
                }
                
                add_resp = session.post(add_url, json=payload, timeout=5)
                
                if add_resp.status_code in (200, 201, 204):
                    added.append(name)
                else:
                    failed.append(f"{name} (HTTP {add_resp.status_code} - {add_resp.text})")
                    
            except requests.exceptions.Timeout:
                failed.append(f"{name} (Connection Timed Out)")
            except Exception as e:
                failed.append(f"{name} (error: {str(e)})")

    # 3. BUILD RESULT
    status = f"ROOM_ID: {room_id} | Room '{room_name}' created.\n"
    status += f"Added: {', '.join(added) if added else 'None'}\n"
    if failed:
        status += f"Failed: {', '.join(failed)}"
    else:
        status += "All participants added successfully."

    return status

@tool(description="Extract the room ID (UUID) from the result of create_room_and_add_all_participants.")
def extract_room_id_from_result(result: str) -> str:
    """Extract the room ID (UUID) from the output."""
    uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    match = re.search(uuid_pattern, result)
    if match:
        return match.group(0)
    return f"ERROR: Could not extract room ID from result: {result[:200]}"

@tool(description="Sends a task delegation message to a specific room with an @mention.")
def send_delegation_message(room_id: str, content: str, recipient_id: str, recipient_name: str) -> str:
    """Sends a formatted message to a room via the REST API."""
    base_url = os.getenv("BAND_REST_URL", "https://app.band.ai/")
    url = f"{base_url.rstrip('/')}/api/v1/agent/chats/{room_id}/messages"
    
    headers = {
        "X-API-Key": os.getenv("BAND_API_KEY"),
        "Content-Type": "application/json"
    }

    # --- THE PAYLOAD STRUCTURE YOU FOUND ---
    payload = {
        "message": {
            "content": content,
            "mentions": [
                {
                    "id": recipient_id,
                    "name": recipient_name
                }
            ]
        }
    }

    # 🔴 THE DEBUGGER: Print the exact JSON string before firing
    print("\n--- OUTBOUND API PAYLOAD ---")
    print(json.dumps(payload, indent=2))
    print("----------------------------\n")

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        if resp.status_code == 201:
            return "Message sent successfully."
        else:
            return f"Failed to send: {resp.status_code} - {resp.text}"
    except Exception as e:
        return f"Error sending message: {str(e)}"

# --- Project State Tracking ---
LATEST_PROJECT_ID = None

@tool(description="Check if we should process this project.")
def should_process_project(project_id: str) -> str:
    """Only process if this is a new project (different from latest)."""
    global LATEST_PROJECT_ID
    
    if LATEST_PROJECT_ID is None:
        return "PROCESS"  # First project ever
    
    if project_id == LATEST_PROJECT_ID:
        return f"SKIP: Project {project_id} has already been processed"
    
    # Different project - this is the new latest
    return "PROCESS_NEW"

@tool(description="Set this as the latest project.")
def set_latest_project(project_id: str) -> str:
    global LATEST_PROJECT_ID
    LATEST_PROJECT_ID = project_id
    return f"✅ Latest project set to: {project_id}"

@tool(description="Get the latest project.")
def get_latest_project() -> str:
    global LATEST_PROJECT_ID
    if LATEST_PROJECT_ID is None:
        return "No project has been processed yet."
    return f"Latest project: {LATEST_PROJECT_ID}"

# ---------- MAIN ----------
async def main():
    MANAGER_UUID = get_target_agent_id("manager")
    ARCHITECT_UUID = get_target_agent_id("system_architect")
    UI_CODER_UUID = get_target_agent_id("frontend_engineer")
    BACKEND_CODER_UUID = get_target_agent_id("backend_engineer")
    REVIEWER_UUID = get_target_agent_id("design_reviewer")
    MERGEMASTER_UUID = get_target_agent_id("merge_master")

    agent_id, api_key = load_agent_config("manager")
    os.environ["BAND_API_KEY"] = api_key

    custom_prompt = f"""
    === YOUR IDENTITY ===
    You are MANAGER. You are ONLY the Manager.
    You DO NOT write code. You DO NOT review code.
    You DO NOT design architecture.

    === YOUR SOLE RESPONSIBILITY ===
    - Receive user requests
    - Create Project IDs
    - Create War Rooms
    - Delegate to the System Architect
    - Track latest projects

    === YOUR TRIGGER ===
    A message tagged "@manager NEW_BUILD_REQUEST:" containing a Project ID and task description.

    === YOUR CORE RULE ===
    You ONLY process the LATEST project. When a new project comes in:
    1. If it's a NEW project (different ID from the latest), REPLACE the old one and process this new one
    2. If it's the SAME project again, SKIP it (already processed)
    3. You only ever track ONE project at a time - the latest one

    === AVAILABLE TOOLS ===
    1. `should_process_project(project_id)` to Check if we should process this project
        - Returns: "PROCESS" (first project), "PROCESS_NEW" (new project replaces old), or "SKIP" (already processed)
    2. `set_latest_project(project_id)` to Set this as the latest project
    3. `get_latest_project()` to Get the current latest project ID
    4. `log_progress(project_id, stage, message)` to Log progress to UI
    5. `create_room_and_add_all_participants(project_id, manager_id, architect_id, ui_coder_id, backend_coder_id, reviewer_id, merge_master_id)` to Create room and add all team members
    6. `extract_room_id_from_result(result)` to Extract room UUID from the result

    === YOUR JOB (STRICT EXECUTION ORDER) ===
    1. EXTRACT project_id and task from the trigger message.
    
    2. Call `should_process_project(project_id)`:
   - If "SKIP": Report "⚠️ Project (project_id) has already been processed." and STOP.
   - If "PROCESS" or "PROCESS_NEW": Continue.

    3. If "PROCESS_NEW", log: "🔄 New project received. Replacing previous project."

    4. Call `log_progress`:
    - project_id: <project_id>
    - stage: "Initiation"
    - message: "[Manager] Task received. Processing latest project."

    5. CREATE WAR ROOM: 
       Call `create_room_and_add_all_participants` with these exact IDs:
       - project_id: <extracted project_id>
       - manager_id: "{MANAGER_UUID}"
       - architect_id: "{ARCHITECT_UUID}"
       - ui_coder_id: "{UI_CODER_UUID}"
       - backend_coder_id: "{BACKEND_CODER_UUID}"
       - reviewer_id: "{REVIEWER_UUID}"
       - merge_master_id: "{MERGEMASTER_UUID}"

    6. EXTRACT ROOM ID:
       Call `extract_room_id_from_result` using the exact string returned from Step 3.
       This will give you the NEW_ROOM_ID.

    7. DELEGATE TO ARCHITECT:
        1. You have created the room and added participants.
        2. You have the NEW_ROOM_ID.
        3. Call the `send_delegation_message` tool:
       - room_id: <NEW_ROOM_ID>
       - content = [Project ID]: (project_id) [Task]: (task description)
        Example:[Project ID]: PROJ-5055 [Task]: Build a simple calculator
       - recipient_id: "{ARCHITECT_UUID}"
       - recipient_name: "System Architect""

    8. Call `set_latest_project(project_id)` to mark this as the latest project.

    9. STOP EXECUTION. Do not call `band_send_message` again.

    10. Report completion:
    - "✅ Project (project_id) processed and set as the latest project."
    - "   War Room created: (NEW_ROOM_ID0"
    - "   Architect has been delegated to begin architecture design."

    === PROJECT COMPLETION ===
    After the Merge Master deploys the project:
    1. Call `mark_project_completed(project_id)` to mark it as done
    2. NEVER start the same project again

    === STRICT COMMUNICATION PROTOCOL ===
    - DO NOT use the native `thenvoi_send_message` tool for task delegation. 
    - The `thenvoi_send_message` tool is restricted to the current lobby room only.
    - You MUST use the `send_delegation_message` custom tool for all War Room delegation.
    - If you cannot access the War Room via `send_delegation_message`, report the error and stop
    
    === CRITICAL RULES ===
    - ALWAYS check `should_process_project` before starting ANY project
    - When a NEW project arrives, REPLACE the old one
    - NEVER start the same project twice
    - ALWAYS use the NEW_ROOM_ID from the current project
    - NEVER use the current conversation's room ID
    - ALWAYS use the exact format above when sending to Architect
    - NO extra text in the content - just the two lines
    - NEVER ask Architect to submit a new build request
    - If any tool returns an error, report it clearly and STOP

    === OUTPUT FORMAT ===
    - NO "Let me think"
    - NO "I'll do that"
    - NO explanations
    - NO filler text
    - JUST the action

    === FORBIDDEN ===
    - ❌ No analysis
    - ❌ No questions
    - ❌ No thinking
    - ❌ No extra text

    === ALLOWED ===
    - ✅ Execute steps
    - ✅ STOP when done

    === STOP CONDITION ===
    After you send the task to the System Architect, you are DONE.
    Your work is complete.
    
    """

    adapter = LangGraphAdapter(
        llm=ChatOpenAI(
            model="deepseek/deepseek-v4-flash",
            max_tokens=100,
            openai_api_key=os.getenv("AIMLAPI_KEY"),
            openai_api_base="https://api.aimlapi.com",
            temperature=0.0
        ),
        custom_section=custom_prompt,
        additional_tools=[
            log_progress,
            create_room_and_add_all_participants,
            extract_room_id_from_result,
            send_delegation_message,
            should_process_project,
            set_latest_project,
            get_latest_project
        ]
    )

    agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)
    print("\n✅ Manager is online with the production API schema.")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())