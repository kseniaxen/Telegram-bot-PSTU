import sqlite3
from typing import Dict, Optional
from datetime import datetime

class Database:
    def __init__(self, db_path: str = 'support_bot.db'):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_questions (
            user_id INTEGER PRIMARY KEY,
            support_msg_id INTEGER,
            question TEXT NOT NULL,
            username TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending'  -- pending, answered, closed
        )
        ''')
        self.conn.commit()

    def add_question(self, user_id: int, support_msg_id: int, question: str, username: str):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO user_questions 
        (user_id, support_msg_id, question, username, status) 
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, support_msg_id, question, username, 'pending'))
        self.conn.commit()

    def get_question(self, user_id: int) -> Optional[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT user_id, support_msg_id, question, username, status 
        FROM user_questions 
        WHERE user_id = ?
        ''', (user_id,))
        row = cursor.fetchone()
        if row:
            return {
                'user_id': row[0],
                'support_msg_id': row[1],
                'question': row[2],
                'username': row[3],
                'status': row[4]
            }
        return None

    def update_question_status(self, user_id: int, status: str):
        cursor = self.conn.cursor()
        cursor.execute('''
        UPDATE user_questions 
        SET status = ? 
        WHERE user_id = ?
        ''', (status, user_id))
        self.conn.commit()

    def remove_question(self, user_id: int):
        cursor = self.conn.cursor()
        cursor.execute('''
        DELETE FROM user_questions 
        WHERE user_id = ?
        ''', (user_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()
