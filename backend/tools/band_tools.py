import os
import requests
import json

def send_band_message(target_agent_id: str, content: str, project_id: str) -> str:

    """
    Sends a task via the Band.ai network to the next agent in the swarm.
    """
    api_key = os.getenv("BAND_API_KEY")
    url = "https://api.band.ai/v1/messages" 
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # We pass the project_id so the next agent knows which codebase to look at
    payload = {
        "to_agent_id": target_agent_id,
        "content": f"[Project: {project_id}]\n\n{content}"
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return f"Successfully handed off to {target_agent_id}."
    except requests.exceptions.RequestException as e:
        return f"Failed to send message via Band.ai: {str(e)}"