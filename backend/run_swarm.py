import subprocess
import sys
import time
import os

from dotenv import load_dotenv

# 1. Dynamically find the absolute path to the backend/ folder
# This ensures it works no matter where you move the folder on laptop
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, ".env")

# 2. Force load_dotenv to read that exact file
load_dotenv(dotenv_path=env_path)

# DEBUG CHECK FOR GOOGLE API KEY
# print(f"DEBUG: Looking for .env at: {env_path}")
# print(f"DEBUG: Did we find the Gemini Key? {'YES' if os.getenv('GEMINI_API_KEY') else 'NO'}")
# print(f"DEBUG: Did we find the Google Key? {'YES' if os.getenv('GOOGLE_API_KEY') else 'NO'}")

# List of your agent scripts based on your directory structure
AGENT_SCRIPTS = [
    "agents/manager.py",
    "agents/system_architect.py",
    "agents/frontend_engineer.py",
    "agents/backend_engineer.py",
    "agents/design_reviewer.py",
    "agents/merge_master.py"
]

processes = []

def start_swarm():
    print("🚀 Booting up the Agent Swarm...")
    for script in AGENT_SCRIPTS:
        print(f"Starting {script}...")
        # Start each script as a separate background process
        p = subprocess.Popen([sys.executable, script])
        processes.append(p)
        # Brief pause to avoid hammering the Band.ai API instantly
        time.sleep(1) 
    
    print("\n✅ All agents are live and listening to Band.ai!")
    print("Press Ctrl+C to shut down the entire swarm.\n")

def shutdown_swarm():
    print("\n🛑 Shutting down the swarm...")
    for p in processes:
        p.terminate()
    print("Shutdown complete.")

if __name__ == "__main__":
    try:
        start_swarm()
        # Keep the main process alive while agents run
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown_swarm()