# backend/tools/db.py
import sqlite3
import os
import json
from datetime import datetime

# Database path - Railway provides persistent volume via /app/data
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "projects.db")

def get_db_connection():
    """Create a connection to the SQLite database."""
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            project_id TEXT PRIMARY KEY,
            task TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            room_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            deployed_url TEXT,
            error_message TEXT
        )
    """)
    
    # Create index for faster lookups
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_project_status ON projects(status)")
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

def get_project_status(project_id: str):
    """Get the status of a project."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM projects WHERE project_id = ?", 
        (project_id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return {"error": "Project not found", "project_id": project_id}

def update_project_status(project_id: str, status: str, **kwargs):
    """Update the status of a project."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build update query dynamically
    updates = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
    values = [status]
    
    for key, value in kwargs.items():
        updates.append(f"{key} = ?")
        values.append(value)
    
    values.append(project_id)
    
    query = f"""
        UPDATE projects 
        SET {', '.join(updates)}
        WHERE project_id = ?
    """
    
    cursor.execute(query, values)
    conn.commit()
    conn.close()
    return True

def create_project(project_id: str, task: str, **kwargs):
    """Create a new project entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    columns = ["project_id", "task"]
    placeholders = ["?", "?"]
    values = [project_id, task]
    
    for key, value in kwargs.items():
        columns.append(key)
        placeholders.append("?")
        values.append(value)
    
    query = f"""
        INSERT INTO projects ({', '.join(columns)})
        VALUES ({', '.join(placeholders)})
    """
    
    try:
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False