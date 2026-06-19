# backend/start_backend.py
import subprocess
import sys
import time
import os
import atexit
import signal

from dotenv import load_dotenv

# Dynamically find the absolute path to the backend/ folder
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, ".env")

load_dotenv(dotenv_path=env_path)

# Railway provides PORT environment variable
PORT = os.getenv("PORT", "8000")
print(f"🚀 Starting on port {PORT}...")

# START THE API SERVER IN THE BACKGROUND
print(f"Starting FastAPI Backend Server on Port {PORT}...")
api_process = subprocess.Popen([sys.executable, "api_server.py"])

# PREVENT GHOST PROCESSES: This ensures that Ctrl+C also kills the API server
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
    print("📍 Railway Service is running...")
    print("Press Ctrl+C to shut down the entire swarm.\n")

def shutdown_swarm():
    print("\n🛑 Shutting down the swarm...")
    for p in processes:
        p.terminate()
    print("Shutdown complete.")

def signal_handler(sig, frame):
    print("\n🛑 Received shutdown signal...")
    shutdown_swarm()
    sys.exit(0)

if __name__ == "__main__":
    try:
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        start_swarm()
        # Keep the main process alive while agents run
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown_swarm()
    except Exception as e:
        print(f"❌ Error: {e}")
        shutdown_swarm()
        sys.exit(1)