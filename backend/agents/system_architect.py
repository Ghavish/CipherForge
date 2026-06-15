import os
import sys
import asyncio
from dotenv import load_dotenv
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
    # load_dotenv()

    # Dynamically fetch the routing IDs
    UI_CODER_UUID = get_target_agent_id("frontend_engineer")
    BACKEND_CODER_UUID = get_target_agent_id("backend_engineer")

    custom_prompt = f"""
    You are the System Architect. When you receive a message from the Manager:
    1. Generate a strict JSON blueprint for the folder structure and database.
    2. Use `send_band_message` TWICE. Once to send the UI tasks to {UI_CODER_UUID}, 
       and once to send the Backend tasks to {BACKEND_CODER_UUID}.
    Always include the Project ID in your messages.
    """

    adapter = LangGraphAdapter(
        
        # llm=ChatOpenAI(model="gemini-1.5-flash"),
        llm=ChatGoogleGenerativeAI(model="gemini-1.5-flash"),
        
        custom_section=custom_prompt,
        additional_tools=[send_band_message]
    )

    agent_id, api_key = load_agent_config("system_architect")
    agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)
    
    print("📐 Architect is online...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())