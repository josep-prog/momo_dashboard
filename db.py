import sqlite3
import os

DB_NAME = 'corrected_data.db'

def init_db():
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Drop existing table if it exists
        c.execute('DROP TABLE IF EXISTS transactions')
        
        # Create new table with name field
        c.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                amount INTEGER,
                date TEXT,
                body TEXT,
                address TEXT,
                readable_date TEXT,
                name TEXT
            )
        ''')
        conn.commit()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise

def store_data(data):
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        for item in data:
            c.execute('''
                INSERT INTO transactions (type, amount, date, body, address, readable_date, name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                item['type'],
                item['amount'],
                item['date'],
                item['body'],
                item['address'],
                item['readable_date'],
                item.get('name')  # Use get() to handle missing name field
            ))
        conn.commit()
        conn.close()
        print(f"Successfully stored {len(data)} transactions")
    except Exception as e:
        print(f"Error storing data: {str(e)}")
        raise

def get_unique_names():
    try:
        if not os.path.exists(DB_NAME):
            raise FileNotFoundError(f"Database file {DB_NAME} not found")
        
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        
        # Get unique non-null names
        names = c.execute('''
            SELECT DISTINCT name 
            FROM transactions 
            WHERE name IS NOT NULL AND name != ''
            ORDER BY name
        ''').fetchall()
        conn.close()

        # Clean names for filter
        cleaned_names = []
        for name in [n[0] for n in names]:
            if not name:
                continue
                
            # Split into words
            words = name.split()
            
            # Skip if not 1-2 words
            if not (1 <= len(words) <= 2):
                continue
                
            # Skip if any word is too short (less than 2 chars)
            if any(len(w) < 2 for w in words):
                continue
                
            # Skip if any word is all uppercase (likely an acronym)
            if any(w.isupper() for w in words):
                continue
                
            # Skip if any word starts with a number
            if any(w[0].isdigit() for w in words):
                continue
                
            common_terms = {
                'payment', 'deposit', 'transfer', 'airtime', 'cash', 'power',
                'agent', 'mtn', 'momo', 'withdraw', 'balance', 'fee', 'bank',
                'completed', 'ref', 'txn', 'id', 'code', 'rwf', 'account',
                'transaction', 'and', 'the', 'of', 'for', 'on', 'in', 'at',
                'to', 'by', 'from', 'with'
            }
            if any(w.lower() in common_terms for w in words):
                continue
                
            # Ensure proper capitalization
            name = ' '.join(w.capitalize() for w in words)
            
            # Add to cleaned names if not already present
            if name not in cleaned_names:
                cleaned_names.append(name)
                
        return sorted(cleaned_names)
    except Exception as e:
        print(f"Error getting unique names: {str(e)}")
        raise
