import sqlite3
from datetime import datetime
from typing import Optional, List, Dict

class Database:
    def __init__(self, db_name: str = "database.db"):
        self.db_name = db_name
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                name TEXT,
                context TEXT,
                birthday DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_or_update_user(self, telegram_id: int, username: str, first_name: str):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (telegram_id, username, first_name, last_active)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(telegram_id) 
            DO UPDATE SET last_active = ?
        ''', (telegram_id, username, first_name, datetime.now(), datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_contact(self, telegram_id: int, name: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, context, birthday, updated_at
            FROM contacts
            WHERE telegram_id = ? AND LOWER(name) = LOWER(?)
        ''', (telegram_id, name))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "id": result[0],
                "name": result[1],
                "context": result[2],
                "birthday": result[3],
                "updated_at": result[4]
            }
        return None
    
    def add_contact(self, telegram_id: int, name: str, content: str, birthday: Optional[str] = None):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
        context = f"[{timestamp}] {content}"
        
        cursor.execute('''
            INSERT INTO contacts (telegram_id, name, context, birthday, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (telegram_id, name, context, birthday, datetime.now()))
        
        conn.commit()
        conn.close()
    
    def update_contact(self, contact_id: int, new_content: str, birthday: Optional[str] = None):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT context FROM contacts WHERE id = ?', (contact_id,))
        current_context = cursor.fetchone()[0]
        
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M")
        updated_context = f"{current_context}\n\n[{timestamp}] {new_content}"
        
        if birthday:
            cursor.execute('''
                UPDATE contacts 
                SET context = ?, birthday = ?, updated_at = ?
                WHERE id = ?
            ''', (updated_context, birthday, datetime.now(), contact_id))
        else:
            cursor.execute('''
                UPDATE contacts 
                SET context = ?, updated_at = ?
                WHERE id = ?
            ''', (updated_context, datetime.now(), contact_id))
        
        conn.commit()
        conn.close()
    
    def get_upcoming_birthdays(self, days_ahead: int = 7) -> List[Dict]:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT telegram_id, name, context, birthday
            FROM contacts
            WHERE birthday IS NOT NULL
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        from datetime import date, timedelta
        today = date.today()
        
        upcoming = []
        for result in results:
            birthday_str = result[3]
            try:
                birthday = datetime.strptime(birthday_str, "%Y-%m-%d").date()
                birthday_this_year = birthday.replace(year=today.year)
                
                if birthday_this_year < today:
                    birthday_this_year = birthday.replace(year=today.year + 1)
                
                days_until = (birthday_this_year - today).days
                
                if 0 <= days_until <= days_ahead:
                    upcoming.append({
                        "telegram_id": result[0],
                        "name": result[1],
                        "context": result[2],
                        "birthday": birthday_str,
                        "days_until": days_until
                    })
            except:
                continue
        
        return upcoming
    
    def get_all_contacts(self, telegram_id: int) -> List[Dict]:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT name, context, birthday
            FROM contacts
            WHERE telegram_id = ?
            ORDER BY name
        ''', (telegram_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {"name": r[0], "context": r[1], "birthday": r[2]}
            for r in results
        ]
