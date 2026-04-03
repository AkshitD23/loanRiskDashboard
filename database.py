import sqlite3
from typing import List, Dict, Any
import datetime

DB_NAME = "loan_risk.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            threshold REAL NOT NULL,
            file_name TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER,
            customer_id TEXT,
            name TEXT,
            probability REAL,
            prediction TEXT,
            FOREIGN KEY (transaction_id) REFERENCES transactions (id)
        )
    ''')
    conn.commit()
    conn.close()

def save_transaction_to_db(threshold: float, file_name: str, predictions: List[Dict[str, Any]]):
    conn = get_connection()
    c = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    
    c.execute('''
        INSERT INTO transactions (timestamp, threshold, file_name)
        VALUES (?, ?, ?)
    ''', (timestamp, threshold, file_name))
    
    transaction_id = c.lastrowid
    
    pred_data = [
        (transaction_id, p.get('id', ''), p.get('name', 'Unknown User'), p.get('probability', 0.0), p.get('prediction', ''))
        for p in predictions
    ]
    
    c.executemany('''
        INSERT INTO predictions (transaction_id, customer_id, name, probability, prediction)
        VALUES (?, ?, ?, ?, ?)
    ''', pred_data)
    
    conn.commit()
    conn.close()
    
    return transaction_id

def get_history_from_db():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''
        SELECT t.id, t.timestamp, t.threshold, t.file_name, COUNT(p.id) as prediction_count
        FROM transactions t
        LEFT JOIN predictions p ON t.id = p.transaction_id
        GROUP BY t.id
        ORDER BY t.timestamp DESC
    ''')
    
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_transaction_details(transaction_id: int):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,))
    transaction = c.fetchone()
    
    if not transaction:
        conn.close()
        return None
        
    c.execute('SELECT * FROM predictions WHERE transaction_id = ?', (transaction_id,))
    predictions = c.fetchall()
    
    conn.close()
    
    return {
        "transaction": dict(transaction),
        "predictions": [dict(p) for p in predictions]
    }
