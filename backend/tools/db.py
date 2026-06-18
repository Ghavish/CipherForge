import sqlite3
import os

# Put the database file in the root of the backend folder
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "swarm_logs.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id TEXT NOT NULL,
            stage TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def append_log(project_id: str, stage: str, message: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO project_logs (project_id, stage, message) VALUES (?, ?, ?)",
        (project_id, stage, message)
    )
    conn.commit()
    conn.close()

def get_project_status(project_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT stage, message FROM project_logs WHERE project_id = ? ORDER BY timestamp ASC",
        (project_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return {"currentStage": "Initializing", "logs": []}

    current_stage = rows[-1][0] 
    logs = [row[1] for row in rows]

    return {"currentStage": current_stage, "logs": logs}