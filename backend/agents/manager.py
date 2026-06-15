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

    adapter = LangGraphAdapter(
        
        # llm=ChatOpenAI(model="gemini-1.5-flash"),
        llm=ChatGoogleGenerativeAI(model="gemini-1.5-flash"),
        
        custom_section=custom_prompt,
        additional_tools=[send_band_message]
    )

    # Note: Ensure "manager" matches the key in agent_config.yaml
    agent_id, api_key = load_agent_config("manager")
    agent = Agent.create(adapter=adapter, agent_id=agent_id, api_key=api_key)
    
    print("🚂 Manager is online and awaiting user requests...")
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())