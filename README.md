🏭 AI Software Factory: Multi-Agent Swarm Builder
Track: Multi-Agent Software Development | Hackathon: Band of Agents (Lablab.ai)

📖 Overview
AI Software Factory is a fully automated, 6-agent orchestration layer designed to handle the entire software development lifecycle. By utilizing Band.ai as the core collaboration protocol, this system ingests user requirements, architects a database and UI hierarchy, writes parallel frontend and backend code, conducts adversarial cross-model QA reviews, and automatically deploys the final product.

🔑 Key Innovations
🔄 Adversarial Model Pairing
We use AI/ML API (DeepSeek) for our high-performance coding agents, and route our Design Reviewer through Claude Opus 4.8. Pitting different neural architectures against each other creates a rigorous self-correction loop that eliminates model-specific blind spots and ensures higher code quality.

🌐 True Band.ai Integration
Agents do not pass Python variables in local memory. The Manager physically schedules tasks, and the System Architect broadcasts architectural blueprints via REST API payloads across the Band.ai network, ensuring true distributed collaboration.

☁️ Hybrid Cloud Architecture
A strictly decoupled React/Next.js frontend (hosted on Vercel) and an asynchronous Python swarm (hosted on Railway/Oracle Cloud) communicate seamlessly through Band.ai's WebSocket and REST APIs.

🗺️ System Architecture

┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                              │ 
│                    React/Next.js (Vercel)                           │
│                   User submits build request                        │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    BAND.AI COLLABORATION LAYER                      │
│              WebSocket + REST API (Real-time Agent Comms)           │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    AGENT SWARM (Python/Railway)                     │
│                                                                     │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────┐              │
│  │ Manager  │───▶│   Architect  │───▶│   Engineers  │              │
│  └──────────┘    └──────────────┘    └───────────────┘              │
│         │                                    │                      │
│         ▼                                    ▼                      │
│  ┌──────────────────┐              ┌──────────────────┐             │
│  │  Design Reviewer │              │  Merge Master    │             │
│  │  (Adversarial QA)│              │  (Deployment)    │             │
│  └──────────────────┘              └──────────────────┘             │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT LAYER                                 │
│              GitHub + Vercel (Live Application)                     │
└─────────────────────────────────────────────────────────────────────┘
📂 Repository Structure & Local Setup
If you are cloning this repository to run the swarm locally, please note that security credentials and configuration files are not committed to GitHub.

You will need to manually create the environment files listed as (Create Locally) below.

text
ai-software-factory/
├── README.md
├── .gitignore               <-- Blocks all .env and config files
│
├── frontend/                <-- Next.js User Interface
│   ├── app/
│   ├── components/
│   ├── package.json
│   └── .env.local           <-- ⚠️ (Create Locally)
│
└── backend/                 <-- Python Agent Swarm
    ├── Dockerfile
    ├── requirements.txt
    ├── docker-compose.yml   <-- For Oracle VPS deployment
    ├── .env                 <-- ⚠️ (Create Locally)
    │
    ├── config/
    │   └── agent_config.yaml <-- ⚠️ (Create Locally: Agent Personas)
    │
    ├── tools/
    │   └── band_tools.py    <-- Band.ai REST API delegation functions
    │
    └── agents/              <-- The 6 distinct Swarm Nodes
        ├── manager.py         # AI/ML API (DeepSeek V4 Flash)
        ├── system_architect.py # AI/ML API (Claude Opus 4.8)
        ├── ui_coder.py         # AI/ML API (DeepSeek V4 Flash)
        ├── backend_coder.py    # AI/ML API (DeepSeek V4 Flash)
        ├── reviewer.py         # Featherless (Adversarial QA with Qwen)
        └── mergemaster.py      # AI/ML API (DeepSeek V4 Flash)

🔐 Environment Variables
Backend (.env) – Create in /backend/
env
# Deployment Credentials
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_github_username
VERCEL_TOKEN=your_vercel_api_token

# Band.ai Configuration
BAND_REST_URL=https://app.band.ai/
BAND_WS_URL=wss://app.band.ai/api/v1/socket/websocket
BAND_API_KEY=your_band_agent_api_key_here

# AI/ML API (Primary LLM Provider)
AIMLAPI_KEY=your_aiml_api_key_here

Agent Configuration (agent_config.yaml) – Create in /backend/
agents:
  manager:
    agent_id: Agent UUID
    api_key: Agent API KEY
  system_architect:
    agent_id: Agent UUID
    api_key: Agent API KEY
  frontend_engineer:
    agent_id: Agent UUID
    api_key: Agent API KEY
  backend_engineer:
    agent_id: Agent UUID
    api_key: Agent API KEY
  design_reviewer:
    agent_id: Agent UUID
    api_key: Agent API KEY
  merge_master:
    agent_id: Agent UUID
    api_key: Agent API KEY

Frontend (.env.local) – Create in /frontend/
BAND_API_URL="https://app.band.ai/api/v1"
BAND_REST_URL="https://app.band.ai/"
BAND_WS_URL="wss://app.band.ai/api/v1/socket/websocket"

# The UUID of the room with Communication agent and Manager
BAND_ROOM_ID="Your band room ID"

# Agents
BAND_AGENT_API_KEY= Communication Agent Api Key
MANAGER_UUID=Manager UUID

# Where Python backend is running, used for the /api/agent endpoint
NEXT_PUBLIC_PYTHON_BACKEND_URL=http://localhost:8000

🚀 Quick Start
1. Clone the Repository
git clone https://github.com/yourusername/ai-software-factory.git
cd ai-software-factory

2. Set Up Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

3. Configure Environment
Copy the .env template above and fill in your API keys

Copy the agent_config.yaml template to /backend/config/

4. Set Up Frontend
cd frontend
npm install

5. Run the Swarm
# Terminal 1: Start the agents and the python server
cd backend
python start_backend.py

# Terminal 2: Start the frontend
cd frontend
npm run dev

6. Deploy with Docker (Optional)
cd backend
docker-compose up -d