import os
import sys
import asyncio
from dotenv import load_dotenv
from thenvoi import Agent
from thenvoi.adapters import OpenAIAdapter
from thenvoi.config import load_agent_config

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.band_tools import send_band_message
from tools.config_parser import get_target_agent_id

async def main():
    load_dotenv()

    REVIEWER_UUID = get_target_agent_id("design_reviewer")

    custom_prompt = f"""
    You are the Backend Coder. When the Architect sends you a blueprint:
    1. Generate the robust Python backend code and database schemas.
    2. Write the code to the local Git worktree.
    3. Once finished, use `send_band_message` to notify the Design Reviewer to inspect your work.
    Reviewer UUID: {REVIEWER_UUID}
    """

    adapter = OpenAIAdapter(
        model="gemini-1.5-flash", # Use the free, high-speed model
        api_key=os.getenv("GOOGLE_AI_STUDIO_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        custom_section=custom_prompt,
        tools=[send_band_message]
    )

    # adapter = OpenAIAdapter(
    #     model="meta-llama/meta-llama-3-70b-instruct",
    #     api_key=os.getenv("AIML_API_KEY"),
    #     base_url="https://api.aimlapi.com/v1",
    #     custom_section=custom_prompt,
    #     tools=[send_band_message] 
    # )

    agent_id, api_key = load_agent_config("backend_engineer")
    agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)
    
    print("⚙️  Backend Coder is online...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())