import subprocess
import sys
import time
import os
import atexit

from dotenv import load_dotenv

# 1. Dynamically find the absolute path to the backend/ folder
# This ensures it works no matter where you move the folder on laptop
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, ".env")

# 2. Force load_dotenv to read that exact file
load_dotenv(dotenv_path=env_path)

# --- 1. START THE API SERVER IN THE BACKGROUND ---
print("Starting FastAPI Backend Server on Port 8000...")
# sys.executable ensures it uses the exact same Python environment
api_process = subprocess.Popen([sys.executable, "api_server.py"])

# --- 2. PREVENT GHOST PROCESSES ---
# This ensures that when you press Ctrl+C to kill run_swarm, it also kills the API server
def cleanup_api_server():
    print("\nShutting down FastAPI server...")
    api_process.terminate()
    api_process.wait()

atexit.register(cleanup_api_server)

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