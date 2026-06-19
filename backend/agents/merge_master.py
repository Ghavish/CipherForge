import os
import sys
import json
import re
import asyncio
import requests
import subprocess

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

@tool
def write_project_files(project_id: str, project_type: str, files: str) -> str:
    """
    Writes generated code files to disk before deployment.

    Args:
        project_id: The project identifier (e.g. PROJ-1001).
        project_type: Either "frontend" or "backend".
                      Files are written to generated-projects/{project_id}-{project_type}/
        files: A JSON string — a list of objects each with:
               - "path": relative file path (e.g. "src/app/page.tsx")
               - "content": full file content as a string

    Returns a success message or error string.
    """
    if not re.match(r'^[A-Z]+-\d+$', project_id):
        return f"Error: Invalid project_id format '{project_id}'. Expected format: PROJ-1234."

    if project_type not in ["frontend", "backend"]:
        return f"Error: project_type must be 'frontend' or 'backend', got '{project_type}'."

    try:
        file_list = json.loads(files)
    except json.JSONDecodeError as e:
        return f"Error: Could not parse files JSON — {str(e)}"

    project_folder = os.path.join(os.getcwd(), "generated-projects", f"{project_id}-{project_type}")
    written = []

    for entry in file_list:
        relative_path = entry.get("path")
        content = entry.get("content")

        if not relative_path or content is None:
            return f"Error: Each entry needs 'path' and 'content'. Got: {entry}"

        full_path = os.path.join(project_folder, relative_path)

        if not os.path.abspath(full_path).startswith(os.path.abspath(project_folder)):
            return f"Error: Path traversal detected for '{relative_path}'."

        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        written.append(relative_path)

    return f"Success: Wrote {len(written)} file(s) to {project_folder}: {written}"


def _push_to_github(repo_name: str, folder: str, github_user: str, github_token: str) -> str | None:
    """
    Creates a GitHub repo and force-pushes the contents of folder to it.
    Returns None on success, or an error string on failure.
    """
    gh_response = requests.post(
        "https://api.github.com/user/repos",
        headers={
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json"
        },
        json={
            "name": repo_name,
            "description": f"AI Generated — {repo_name}",
            "private": False,
            "auto_init": False
        }
    )

    if gh_response.status_code not in [201, 422]:
        return f"GitHub Error for {repo_name}: {gh_response.json().get('message')}"

    # Use netrc to avoid token in process list
    netrc_path = os.path.expanduser("~/.netrc")
    with open(netrc_path, "w") as f:
        f.write(f"machine github.com login {github_user} password {github_token}\n")
    os.chmod(netrc_path, 0o600)

    remote_url = f"https://github.com/{github_user}/{repo_name}.git"

    git_steps = [
        ["git", "init"],
        ["git", "checkout", "-b", "main"],
        ["git", "add", "."],
        ["git", "commit", "-m", "AI Builder Automated Build"],
        ["git", "remote", "remove", "origin"],
        ["git", "remote", "add", "origin", remote_url],
        ["git", "push", "-u", "origin", "main", "--force"],
    ]

    for step in git_steps:
        result = subprocess.run(step, cwd=folder, capture_output=True, text=True)
        if result.returncode != 0 and step[1] != "remote":
            return f"Git Error at '{' '.join(step)}': {result.stderr}"

    return None

@tool
def deploy_generated_code(project_id: str) -> str:
    """
    Deploys a generated project:
    - Frontend (PROJ-1001-frontend) → GitHub + Vercel
    - Backend  (PROJ-1001-backend)  → GitHub only

    Call write_project_files for both frontend and backend before calling this.

    Args:
        project_id: The project identifier (e.g. PROJ-1001).

    Returns a deployment summary with URLs.
    """
    if not re.match(r'^[A-Z]+-\d+$', project_id):
        return f"Error: Invalid project_id format '{project_id}'."

    github_token = os.getenv("GITHUB_TOKEN")
    github_user = os.getenv("GITHUB_USERNAME")
    vercel_token = os.getenv("VERCEL_TOKEN")

    if not all([github_token, github_user, vercel_token]):
        return "Error: Missing deployment credentials (GITHUB_TOKEN, GITHUB_USERNAME, or VERCEL_TOKEN)."

    base = os.path.join(os.getcwd(), "generated-projects")
    frontend_folder = os.path.join(base, f"{project_id}-frontend")
    backend_folder = os.path.join(base, f"{project_id}-backend")

    results = []

    # --- Frontend: GitHub + Vercel ---
    if not os.path.exists(frontend_folder):
        results.append(f"Frontend Error: folder not found at {frontend_folder}.")
    else:
        frontend_repo = f"{project_id}-frontend".lower()
        err = _push_to_github(frontend_repo, frontend_folder, github_user, github_token)
        if err:
            results.append(err)
        else:
            v_response = requests.post(
                "https://api.vercel.com/v11/projects",
                headers={
                    "Authorization": f"Bearer {vercel_token}",
                    "Content-Type": "application/json"
                },
                json={
                    "name": frontend_repo,
                    "framework": "nextjs",
                    "gitRepository": {
                        "type": "github",
                        "repo": f"{github_user}/{frontend_repo}"
                    }
                }
            )

            if v_response.status_code in [200, 201]:
                data = v_response.json()
                aliases = data.get("alias", [])
                live_url = f"https://{aliases[0]}" if aliases else f"https://{frontend_repo}.vercel.app"
                results.append(f"Frontend deployed. Live URL: {live_url}")
            else:
                results.append(f"Frontend pushed to GitHub but Vercel failed: {v_response.json().get('message')}")

    # --- Backend: GitHub only ---
    if not os.path.exists(backend_folder):
        # ✅ CHANGED: Do not throw an error. Acknowledge it was intentionally skipped.
        results.append("Backend deployment skipped (no backend required).")
    else:
        backend_repo = f"{project_id}-backend".lower()
        err = _push_to_github(backend_repo, backend_folder, github_user, github_token)
        if err:
            results.append(err)
        else:
            results.append(f"Backend pushed to GitHub: https://github.com/{github_user}/{backend_repo}")

    return "\n".join(results)


async def main():
    
    custom_prompt = """
    === YOUR IDENTITY ===
    You are MERGE MASTER. You are ONLY the Merge Master.
    You DO NOT write code. You DO NOT review code.
    You DO NOT design architecture.

    === YOUR SOLE RESPONSIBILITY ===
    - Deploy approved code to GitHub and Vercel
    - Notify the Manager of completion
    - DEPLOY code. That's it. Nothing else.

    === YOUR TRIGGER ===
    A message from the QA Reviewer with [Status]: Approved, a [Project ID], [Frontend Code], and [Backend Code].

    === YOUR JOB (STRICT ORDER) ===
    1. Call the `write_project_files` tool for the frontend:
       project_id=<id>, project_type="frontend", files=<frontend files>

    2. Check the [Backend Code]. IF it is NOT "NONE", call `write_project_files` for the backend:
       project_id=<id>, project_type="backend", files=<backend files>

    3. Call the `deploy_generated_code` tool with the Project ID.

   === PROGRESS LOGGING (MANDATORY) ===
    When `deploy_generated_code` returns, you MUST use the `log_progress` tool:
    - project_id: The ID you received.
    - stage: "Deployment"
    - message: "[Merge Master] Files committed and deployment pipeline executed successfully."

    === THE HANDOFF ===
    Finally, call `band_send_message` ONCE with:
    - content: "[From]: Merge Master\\n[Project ID]: <id>\\n[Status]: DEPLOYMENT COMPLETE\\n[Result]: <full output from deploy_generated_code>"
    - mentions: []

    === HARD RULES ===
    - Execute your tools in the exact order specified.
    - Stop execution after `band_send_message` returns success.
    - You are ONLY the Merge Master.
    - You DO NOT write code.
    - You DO NOT review code.
    - You DO NOT design architecture.
    - After deployment, STOP.
    
    === OUTPUT FORMAT ===
    - NO "Let me think"
    - NO "I'll do that"
    - NO explanations
    - NO filler text
    - JUST the action

    === FORBIDDEN ===
    - ❌ No code review
    - ❌ No questions
    - ❌ No analysis
    - ❌ No thinking

    === STOP CONDITION ===
    After you notify the Manager of deployment completion, you are DONE.
    Your work is complete.
    """

    agent_id, api_key = load_agent_config("merge_master")
    os.environ["BAND_API_KEY"] = api_key

    # AI/ML API
    adapter = LangGraphAdapter(
        llm=ChatOpenAI(
            model="deepseek/deepseek-v4-flash",
            max_tokens=100,
            openai_api_key=os.getenv("AIMLAPI_KEY"),
            openai_api_base="https://api.aimlapi.com",
            temperature=0.0  # Deterministic = faster
        ),
        custom_section=custom_prompt,
        additional_tools=[write_project_files, deploy_generated_code,log_progress]
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
    #     additional_tools=[write_project_files, deploy_generated_code, log_progress]
    # )

    agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)
    print("Merge Master is online...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
