import sqlite3
import os
import json
from datetime import datetime

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database")
DB_PATH = os.path.join(DB_DIR, "history.db")

def get_db_connection():
    """Establish and return a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    # Return rows as dictionary-like objects
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the SQLite database and create prompt_history table if it doesn't exist."""
    # Ensure database directory exists
    os.makedirs(DB_DIR, exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create prompt history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prompt_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_prompt TEXT NOT NULL,
            optimized_prompt TEXT NOT NULL,
            model TEXT NOT NULL,
            category TEXT NOT NULL,
            tone TEXT NOT NULL,
            length TEXT NOT NULL,
            score INTEGER NOT NULL,
            score_details TEXT NOT NULL, -- JSON string of detailed scores
            why_better TEXT NOT NULL,    -- JSON string of why it is better
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_favorite INTEGER DEFAULT 0 -- 0 for False, 1 for True
        )
    """)
    
    conn.commit()
    conn.close()

def save_prompt(original_prompt, optimized_prompt, model, category, tone, length, score, score_details, why_better):
    """Save an optimized prompt entry into the history database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Convert dictionaries to JSON strings if they aren't already strings
    if isinstance(score_details, dict):
        score_details = json.dumps(score_details)
    if isinstance(why_better, dict):
        why_better = json.dumps(why_better)
        
    cursor.execute("""
        INSERT INTO prompt_history (
            original_prompt, optimized_prompt, model, category, tone, length, score, score_details, why_better, created_at, is_favorite
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (
        original_prompt, 
        optimized_prompt, 
        model, 
        category, 
        tone, 
        length, 
        int(score), 
        score_details, 
        why_better,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    
    inserted_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return inserted_id

def get_history(search_query=None, filter_category=None, filter_model=None, only_favorites=False):
    """Retrieve filtered and searched prompt history from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM prompt_history WHERE 1=1"
    params = []
    
    if search_query:
        query += " AND (original_prompt LIKE ? OR optimized_prompt LIKE ?)"
        like_query = f"%{search_query}%"
        params.extend([like_query, like_query])
        
    if filter_category and filter_category != "All":
        query += " AND category = ?"
        params.append(filter_category)
        
    if filter_model and filter_model != "All":
        query += " AND model = ?"
        params.append(filter_model)
        
    if only_favorites:
        query += " AND is_favorite = 1"
        
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    # Convert Row objects to dictionaries and parse JSON fields
    results = []
    for row in rows:
        item = dict(row)
        try:
            item["score_details"] = json.loads(item["score_details"])
        except (TypeError, json.JSONDecodeError):
            item["score_details"] = {}
            
        try:
            item["why_better"] = json.loads(item["why_better"])
        except (TypeError, json.JSONDecodeError):
            item["why_better"] = {}
            
        results.append(item)
        
    conn.close()
    return results

def delete_prompt(prompt_id):
    """Delete a prompt entry by its database ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM prompt_history WHERE id = ?", (prompt_id,))
    conn.commit()
    conn.close()

def toggle_favorite(prompt_id):
    """Toggle the favorite status of a prompt entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get current favorite status
    cursor.execute("SELECT is_favorite FROM prompt_history WHERE id = ?", (prompt_id,))
    row = cursor.fetchone()
    if row:
        current_status = row["is_favorite"]
        new_status = 1 if current_status == 0 else 0
        cursor.execute("UPDATE prompt_history SET is_favorite = ? WHERE id = ?", (new_status, prompt_id))
        conn.commit()
        conn.close()
        return new_status
    conn.close()
    return None

def get_stats():
    """Retrieve statistical aggregations for the stats dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    # Total Prompts
    cursor.execute("SELECT COUNT(*) as count FROM prompt_history")
    stats["total_prompts"] = cursor.fetchone()["count"]
    
    # Average Quality Score
    cursor.execute("SELECT AVG(score) as avg_score FROM prompt_history")
    row = cursor.fetchone()
    stats["avg_score"] = round(row["avg_score"], 1) if row and row["avg_score"] is not None else 0.0
    
    # Most Used Category
    cursor.execute("SELECT category, COUNT(*) as count FROM prompt_history GROUP BY category ORDER BY count DESC LIMIT 1")
    row = cursor.fetchone()
    stats["most_used_category"] = row["category"] if row else "None"
    
    # Favorites Count
    cursor.execute("SELECT COUNT(*) as count FROM prompt_history WHERE is_favorite = 1")
    stats["favorites_count"] = cursor.fetchone()["count"]
    
    # Category Distribution (for charts)
    cursor.execute("SELECT category, COUNT(*) as count, AVG(score) as avg_score FROM prompt_history GROUP BY category")
    stats["category_distribution"] = [dict(r) for r in cursor.fetchall()]
    
    # Optimization Trend over days (last 14 days)
    cursor.execute("""
        SELECT strftime('%Y-%m-%d', created_at) as date, COUNT(*) as count 
        FROM prompt_history 
        GROUP BY date 
        ORDER BY date DESC 
        LIMIT 14
    """)
    stats["trend"] = [dict(r) for r in cursor.fetchall()]
    
    # Recent Prompts
    cursor.execute("SELECT * FROM prompt_history ORDER BY created_at DESC LIMIT 5")
    recent_rows = cursor.fetchall()
    recent = []
    for r in recent_rows:
        item = dict(r)
        try:
            item["score_details"] = json.loads(item["score_details"])
        except:
            item["score_details"] = {}
        recent.append(item)
    stats["recent_prompts"] = recent
    
    conn.close()
    return stats
