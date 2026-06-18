from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tools.db import init_db, get_project_status
import uvicorn

app = FastAPI()

# Allow Next.js frontend to poll this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the SQLite file when the server boots
init_db()

@app.get("/status/{project_id}")
def read_status(project_id: str):
    return get_project_status(project_id)

if __name__ == "__main__":
    print("Starting Swarm API Server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)