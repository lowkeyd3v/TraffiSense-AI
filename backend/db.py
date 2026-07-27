import sqlite3
import os
from typing import List, Dict, Any, Optional

DB_PATH = "db.sqlite3"

def init_db():
    """Initializes the SQLite database with the deployments table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deployments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_cause TEXT,
            veh_type TEXT,
            corridor TEXT,
            priority TEXT,
            time TEXT,
            requires_road_closure INTEGER,
            event_type TEXT,
            latitude REAL,
            longitude REAL,
            police_station TEXT,
            description TEXT,
            event_scale TEXT,
            crowd_size INTEGER,
            predicted_duration REAL,
            personnel INTEGER,
            barricades INTEGER,
            congestion_radius_meters REAL,
            commuter_delay_minutes REAL,
            status TEXT DEFAULT 'active', -- 'active' or 'resolved'
            actual_duration REAL,
            actual_personnel INTEGER,
            actual_barricades INTEGER,
            actual_congestion_radius REAL,
            actual_delay REAL,
            feedback_comments TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_deployment(data: Dict[str, Any], predictions: Dict[str, Any]) -> int:
    """Inserts a new deployment log entry into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
        INSERT INTO deployments (
            event_cause, veh_type, corridor, priority, time, requires_road_closure,
            event_type, latitude, longitude, police_station, description,
            event_scale, crowd_size, predicted_duration, personnel, barricades,
            congestion_radius_meters, commuter_delay_minutes, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active')
    """
    
    cursor.execute(query, (
        data.get("event_cause"),
        data.get("veh_type"),
        data.get("corridor"),
        data.get("priority"),
        data.get("time"),
        1 if data.get("requires_road_closure") else 0,
        data.get("event_type"),
        data.get("latitude"),
        data.get("longitude"),
        data.get("police_station"),
        data.get("description"),
        data.get("event_scale", "Medium"),
        data.get("crowd_size", 0),
        predictions.get("predicted_duration"),
        predictions.get("personnel"),
        predictions.get("barricades"),
        predictions.get("congestion_radius_meters"),
        predictions.get("commuter_delay_minutes")
    ))
    
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id

def get_deployments(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves deployments from the database, optionally filtered by status."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if status:
        cursor.execute("SELECT * FROM deployments WHERE status = ? ORDER BY created_at DESC", (status,))
    else:
        cursor.execute("SELECT * FROM deployments ORDER BY created_at DESC")
        
    rows = cursor.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        d = dict(r)
        d["requires_road_closure"] = bool(d["requires_road_closure"])
        result.append(d)
    return result

def resolve_deployment(deployment_id: int, feedback: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Updates an active deployment with actual metrics and sets status to resolved."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check if exists
    cursor.execute("SELECT * FROM deployments WHERE id = ?", (deployment_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
        
    query = """
        UPDATE deployments
        SET status = 'resolved',
            actual_duration = ?,
            actual_personnel = ?,
            actual_barricades = ?,
            actual_congestion_radius = ?,
            actual_delay = ?,
            feedback_comments = ?
        WHERE id = ?
    """
    
    cursor.execute(query, (
        feedback.get("actual_duration"),
        feedback.get("actual_personnel"),
        feedback.get("actual_barricades"),
        feedback.get("actual_congestion_radius"),
        feedback.get("actual_delay"),
        feedback.get("feedback_comments"),
        deployment_id
    ))
    
    # Fetch updated row
    cursor.execute("SELECT * FROM deployments WHERE id = ?", (deployment_id,))
    updated_row = dict(cursor.fetchone())
    updated_row["requires_road_closure"] = bool(updated_row["requires_road_closure"])
    
    conn.commit()
    conn.close()
    return updated_row
