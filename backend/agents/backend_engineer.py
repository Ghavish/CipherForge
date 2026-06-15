import os
import sys
import asyncio

from thenvoi import Agent
from thenvoi.adapters import LangGraphAdapter
from thenvoi.config import load_agent_config

# from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.checkpoint.memory import InMemorySaver

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.band_tools import send_band_message
from tools.config_parser import get_target_agent_id

async def main():

    REVIEWER_UUID = get_target_agent_id("design_reviewer")

    custom_prompt = f"""
    You are the Backend Coder. When the Architect sends you a blueprint:
    1. Generate the robust Python backend code and database schemas.
    2. Write the code to the local Git worktree.
    3. Once finished, use `send_band_message` to notify the Design Reviewer to inspect your work.
    Reviewer UUID: {REVIEWER_UUID}
    """

    adapter = LangGraphAdapter(
        
        # llm=ChatOpenAI(model="gemini-1.5-flash"),
        llm=ChatGoogleGenerativeAI(model="gemini-1.5-flash"),
        
        custom_section=custom_prompt,
        additional_tools=[send_band_message]
    )
 
    agent_id, api_key = load_agent_config("backend_engineer")
    agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)
    
    print("⚙️  Backend Coder is online...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())