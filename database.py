import psycopg2
import os
from datetime import datetime, timedelta

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        self.cursor = self.conn.cursor()
        self.create_tables()
    
    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                is_vip BOOLEAN DEFAULT FALSE,
                vip_expiry DATE,
                daily_checks INTEGER DEFAULT 0,
                last_check DATE,
                joined_date DATE DEFAULT CURRENT_DATE
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                contract_address TEXT,
                result TEXT,
                scan_date DATE DEFAULT CURRENT_DATE,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS verification_requests (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                email TEXT,
                status TEXT DEFAULT 'pending',
                request_date DATE DEFAULT CURRENT_DATE,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        self.conn.commit()
    
    def add_user(self, user_id, username, first_name):
        self.cursor.execute('''
            INSERT INTO users (user_id, username, first_name)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id) DO NOTHING
        ''', (user_id, username, first_name))
        self.conn.commit()
    
    def get_user(self, user_id):
        self.cursor.execute('SELECT * FROM users WHERE user_id = %s', (user_id,))
        return self.cursor.fetchone()
    
    def is_vip(self, user_id):
        user = self.get_user(user_id)
        if not user:
            return False
        if not user[3]:
            return False
        expiry = user[4]
        if expiry is None:
            return False
        return expiry >= datetime.now().date()
    
    def activate_vip(self, user_id, days=30):
        expiry = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        self.cursor.execute('''
            UPDATE users SET is_vip = TRUE, vip_expiry = %s
            WHERE user_id = %s
        ''', (expiry, user_id))
        self.conn.commit()
    
    def can_check(self, user_id):
        if self.is_vip(user_id):
            return True
        user = self.get_user(user_id)
        today = datetime.now().date()
        if not user:
            return True
        last_check = user[6]
        daily_checks = user[5]
        if last_check != str(today):
            self.cursor.execute('''
                UPDATE users SET daily_checks = 1, last_check = %s
                WHERE user_id = %s
            ''', (str(today), user_id))
            self.conn.commit()
            return True
        return daily_checks < 3
    
    def increment_check(self, user_id):
        self.cursor.execute('''
            UPDATE users SET daily_checks = daily_checks + 1
            WHERE user_id = %s
        ''', (user_id,))
        self.conn.commit()
    
    def add_verification_request(self, user_id, email):
        self.cursor.execute('''
            INSERT INTO verification_requests (user_id, email)
            VALUES (%s, %s)
        ''', (user_id, email))
        self.conn.commit()
    
    def get_pending_verifications(self):
        self.cursor.execute('''
            SELECT vr.user_id, vr.email, u.first_name, u.username
            FROM verification_requests vr
            JOIN users u ON vr.user_id = u.user_id
            WHERE vr.status = 'pending'
        ''')
        return self.cursor.fetchall()
    
    def close(self):
        try:
            self.cursor.close()
            self.conn.close()
        except:
            pass
