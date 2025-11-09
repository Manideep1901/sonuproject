import sqlite3
import hashlib
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('expense_tracker.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create expenses table with user_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            mood TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# User management functions
def create_user(username, password, email=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        cursor.execute(
            'INSERT INTO users (username, password, email) VALUES (?, ?, ?)',
            (username, hashed_password, email)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def verify_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    cursor.execute(
        'SELECT id, username FROM users WHERE username = ? AND password = ?',
        (username, hashed_password)
    )
    
    user = cursor.fetchone()
    conn.close()
    
    return dict(user) if user else None

# Updated expense functions with user_id
def add_expense(user_id, date, category, amount, description, mood):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO expenses (user_id, date, category, amount, description, mood) VALUES (?, ?, ?, ?, ?, ?)',
        (user_id, date, category, amount, description, mood)
    )
    
    conn.commit()
    conn.close()

def get_all_expenses(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT date, category, amount, description, mood FROM expenses WHERE user_id = ? ORDER BY date DESC',
        (user_id,)
    )
    
    expenses = cursor.fetchall()
    conn.close()
    
    return [dict(expense) for expense in expenses]

def get_spending_by_mood(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT mood, SUM(amount) as total_amount FROM expenses WHERE user_id = ? GROUP BY mood',
        (user_id,)
    )
    
    results = cursor.fetchall()
    conn.close()
    
    return [dict(result) for result in results]

def get_spending_by_category_mood(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT mood, category, SUM(amount) as total_amount FROM expenses WHERE user_id = ? GROUP BY mood, category',
        (user_id,)
    )
    
    results = cursor.fetchall()
    conn.close()
    
    return [dict(result) for result in results]

def get_eco_impact_by_mood(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        '''SELECT mood, category, SUM(amount) as total_amount 
           FROM expenses WHERE user_id = ? GROUP BY mood, category''',
        (user_id,)
    )
    
    results = cursor.fetchall()
    conn.close()
    
    return [dict(result) for result in results]