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

    # Dynamically look up the Architect's ID
    ARCHITECT_UUID = get_target_agent_id("system_architect")

    # Refined prompt for ID enforcement
    custom_prompt = f"""
    You are the Manager. Your task is to orchestrate the software development lifecycle.
    
    Workflow:
    1. When a user provides a request, generate a unique Project ID (format: PROJ-XXXX).
    2. Immediately use the `send_band_message` tool to hand off the project.
    3. You must include the generated Project ID in the `project_id` parameter of the tool.
    
    Architect UUID: {ARCHITECT_UUID}
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

    # Note: Ensure "manager" matches the key in your config/agent_config.yaml
    agent_id, api_key = load_agent_config("manager")
    agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)
    
    print("🚂 Conductor is online and awaiting user requests...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())