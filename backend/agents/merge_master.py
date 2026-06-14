import os
import asyncio
from dotenv import load_dotenv
from thenvoi import Agent
from thenvoi.adapters import OpenAIAdapter
from thenvoi.config import load_agent_config

async def main():
    load_dotenv()

    custom_prompt = """
    You are the Mergemaster. When the Reviewer approves a project ID:
    1. Execute terminal commands to commit the files to the active Git branch.
    2. Push to the remote repository to trigger the deployment.
    """

    adapter = OpenAIAdapter(
        model="gemini-1.5-flash", # Use the free, high-speed model
        api_key=os.getenv("GOOGLE_AI_STUDIO_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        custom_section=custom_prompt
    )

    # adapter = OpenAIAdapter(
    #     model="meta-llama/meta-llama-3-70b-instruct",
    #     api_key=os.getenv("AIML_API_KEY"),
    #     base_url="https://api.aimlapi.com/v1",
    #     custom_section=custom_prompt
    # )

    agent_id, api_key = load_agent_config("merge_master")
    agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)
    
    print("🚀 Mergemaster is online...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())