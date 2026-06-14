# 🏭 AI Software Factory: Multi-Agent Swarm Builder


**Track:** Multi-Agent Software Development | **Hackathon:** Band of Agents (Lablab.ai)

## 📖 Overview
AI Software Factory is a fully automated, 6-agent orchestration layer designed to handle the entire software development lifecycle. By utilizing **Band.ai** as the core collaboration protocol, this system ingests user requirements, architects a database and UI hierarchy, writes parallel frontend and backend code, conducts adversarial cross-model QA reviews, and automatically deploys the final product.

### 🔑 Key Innovations
* **Adversarial Model Pairing:** We use AI/ML API (Llama-3) for our highly-performant coding agents, but route our Design Reviewer through Featherless (Qwen/DeepSeek). Pitting different neural architectures against each other creates a rigorous self-correction loop that eliminates model-specific blind spots.

* **True Band.ai Integration:** Agents do not pass Python variables in local memory. The Conductor physically schedules tasks, and the Planners broadcast architectural blueprints via REST API payloads across the Band.ai network. 

* **Hybrid Cloud Architecture:** A strictly decoupled React/Next.js frontend (hosted on Vercel) and an asynchronous Python swarm (hosted on Railway/Oracle Cloud).

---

## 🗺️ System Architecture

*(Include architecture diagram here explaining how Vercel, Oracle Cloud/Railway, and Band.ai connect)*
`[Image placeholder: Architecture Diagram]`

---

## 📂 Repository Structure & Local Setup

If you are cloning this repository to run the swarm locally, please note that **security credentials and configuration files are not committed to GitHub**. 

You will need to manually create the environment files listed as `(Create Locally)` below.

```text
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
        ├── manager.py         # AI/ML API
        ├── system_architect.py  # AI/ML API
        ├── ui_coder.py          # AI/ML API
        ├── backend_coder.py     # AI/ML API
        ├── reviewer.py          # Featherless (Adversarial QA)
        └── mergemaster.py       # AI/ML API

