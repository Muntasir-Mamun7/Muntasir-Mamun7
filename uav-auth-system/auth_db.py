"""
Database module for UAV Authentication System
Handles user registration, authentication, and session management
"""
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
import os

class AuthDB:
    def __init__(self, db_path='uav_auth.db'):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database with users and sessions tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """
        Hash password using SHA-256
        
        NOTE: For production use, replace with bcrypt, scrypt, or argon2:
        - pip install bcrypt
        - import bcrypt
        - return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        
        SHA-256 is used here for simplicity but is vulnerable to rainbow
        table attacks without proper salting.
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password):
        """Register a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            cursor.execute(
                'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                (username, password_hash)
            )
            
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return True, user_id
        except sqlite3.IntegrityError:
            return False, "Username already exists"
        except Exception as e:
            return False, str(e)
    
    def authenticate_user(self, username, password):
        """Authenticate user and return user info"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        cursor.execute(
            'SELECT id, username FROM users WHERE username = ? AND password_hash = ?',
            (username, password_hash)
        )
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return True, {'id': user[0], 'username': user[1]}
        return False, "Invalid credentials"
    
    def create_session(self, user_id):
        """Create a new session token for user"""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=24)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)',
            (user_id, token, expires_at.isoformat())
        )
        
        conn.commit()
        conn.close()
        
        return token
    
    def validate_session(self, token):
        """Validate session token and return user info"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT u.id, u.username, s.expires_at 
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ?
        ''', (token,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            user_id, username, expires_at = result
            if datetime.fromisoformat(expires_at) > datetime.now():
                return True, {'id': user_id, 'username': username}
            else:
                # Session expired
                self.invalidate_session(token)
                return False, "Session expired"
        
        return False, "Invalid token"
    
    def invalidate_session(self, token):
        """Invalidate a session token (logout)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sessions WHERE token = ?', (token,))
        
        conn.commit()
        conn.close()
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'DELETE FROM sessions WHERE expires_at < ?',
            (datetime.now().isoformat(),)
        )
        
        conn.commit()
        conn.close()
