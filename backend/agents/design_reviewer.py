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

    UI_CODER_UUID = get_target_agent_id("frontend_engineer")
    BACKEND_CODER_UUID = get_target_agent_id("backend_engineer")
    MERGEMASTER_UUID = get_target_agent_id("merge_master")

    custom_prompt = f"""
    You are a ruthless Quality Assurance Agent. When coders send you finished work:
    1. Inspect it for syntax errors, logical flaws, and strict adherence to aesthetic rules.
    2. IF THERE ARE FRONTEND ERRORS: Use `send_band_message` to send the file back to {UI_CODER_UUID}.
    3. IF THERE ARE BACKEND ERRORS: Use `send_band_message` to route back to {BACKEND_CODER_UUID}.
    4. IF PERFECT: Use `send_band_message` to alert the Mergemaster ({MERGEMASTER_UUID}) that it is approved for deployment.
    """

    
    adapter = OpenAIAdapter(
        model="gemini-1.5-flash", # Use the free, high-speed model
        api_key=os.getenv("GOOGLE_AI_STUDIO_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        custom_section=custom_prompt,
        tools=[send_band_message]
    )
    
    # Routing to Featherless for Adversarial Model Pairing
    # adapter = OpenAIAdapter(
    #     model="Qwen/Qwen2-72B-Instruct", 
    #     api_key=os.getenv("FEATHERLESS_API_KEY"),
    #     base_url="https://api.featherless.ai/v1",
    #     custom_section=custom_prompt,
    #     tools=[send_band_message],
    #     enable_execution_reporting=True
    # )

    agent_id, api_key = load_agent_config("design_reviewer")
    agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)
    
    print("🛡️  Reviewer (Featherless QA) is online...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())