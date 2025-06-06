from flask import Flask, render_template, request, jsonify
import xml.etree.ElementTree as ET
import sqlite3
import re
import os
from datetime import datetime

app = Flask(__name__)

DB_FILE = "momo.db"
XML_FILE = "modified_sms_v2.xml"

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    try:
        conn = get_db()
        with open("schema.sql") as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
        print("Database initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False

def extract_transaction_id(text):
    match = re.search(r'[Tt]x[Ii]d:?\s*(\d+)', text)
    return match.group(1) if match else None

def extract_fee(text):
    match = re.search(r'[Ff]ee:?\s*(\d+)', text)
    return int(match.group(1)) if match else 0

def process_xml():
    try:
        if not os.path.exists(XML_FILE):
            print(f"Error: XML file {XML_FILE} not found")
            return False

        tree = ET.parse(XML_FILE)
        root = tree.getroot()
        
        categories = {
            "received": r"you have received (\d+) rwf",
            "payment": r"your payment of (\d+) rwf",
            "deposit": r"bank deposit of (\d+) rwf",
            "withdrawal": r"withdrawn (\d+) rwf",
            "bundle": r"internet bundle",
            "cashpower": r"cash power",
        }

        conn = get_db()
        cur = conn.cursor()

        # Clear existing data
        cur.execute("DELETE FROM transactions")
        
        for sms in root.findall("sms"):
            body = sms.get("body", "").lower()
            date = sms.get("readable_date")
            
            if not body or not date:
                continue

            for t, pattern in categories.items():
                if re.search(pattern, body):
                    amount_match = re.search(r"(\d{3,}) rwf", body)
                    person_match = re.search(r"from (.*?)\(|to (.*?)\d{2,}", body)
                    
                    amount = int(amount_match.group(1)) if amount_match else 0
                    person = person_match.group(1) if person_match else "unknown"
                    tx_id = extract_transaction_id(body)
                    fee = extract_fee(body)

                    cur.execute('''
                        INSERT INTO transactions (type, amount, person, date, transaction_id, fee, raw_sms)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (t, amount, person.strip(), date, tx_id, fee, body))
                    break

        conn.commit()
        conn.close()
        print("XML data processed successfully")
        return True
    except Exception as e:
        print(f"Error processing XML: {e}")
        return False

def ensure_db_exists():
    if not os.path.exists(DB_FILE):
        print("Database file not found. Initializing...")
        if not init_db():
            return False
    else:
        # Verify if table exists
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
            if not cur.fetchone():
                print("Transactions table not found. Initializing...")
                if not init_db():
                    return False
            conn.close()
        except Exception as e:
            print(f"Error checking database: {e}")
            return False
    return True

@app.route("/")
def dashboard():
    if not ensure_db_exists():
        return "Error: Database initialization failed", 500
    return render_template("index.html")

@app.route("/api/data")
def get_data():
    if not ensure_db_exists():
        return jsonify({"success": False, "error": "Database not initialized"}), 500

    try:
        conn = get_db()
        cur = conn.cursor()
        
        q = request.args.get("q", "")
        type_filter = request.args.get("type", "")
        date_from = request.args.get("from", "")
        date_to = request.args.get("to", "")

        query = "SELECT * FROM transactions WHERE 1=1"
        params = []

        if q:
            query += " AND (type LIKE ? OR person LIKE ? OR transaction_id LIKE ?)"
            params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
        
        if type_filter:
            query += " AND type = ?"
            params.append(type_filter)
        
        if date_from:
            query += " AND date >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND date <= ?"
            params.append(date_to)

        query += " ORDER BY date DESC"
        
        cur.execute(query, params)
        data = [dict(row) for row in cur.fetchall()]
        conn.close()
        
        return jsonify({"success": True, "data": data})
    except Exception as e:
        print(f"Error fetching data: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/summary")
def get_summary():
    if not ensure_db_exists():
        return jsonify({"success": False, "error": "Database not initialized"}), 500

    try:
        conn = get_db()
        cur = conn.cursor()
        
        # Get transaction counts by type
        cur.execute("""
            SELECT type, COUNT(*) as count, SUM(amount) as total_amount
            FROM transactions
            GROUP BY type
        """)
        type_summary = [dict(row) for row in cur.fetchall()]
        
        # Get total transactions and amount
        cur.execute("""
            SELECT COUNT(*) as total_transactions, SUM(amount) as total_amount
            FROM transactions
        """)
        overall_summary = dict(cur.fetchone())
        
        conn.close()
        
        return jsonify({
            "success": True,
            "type_summary": type_summary,
            "overall_summary": overall_summary
        })
    except Exception as e:
        print(f"Error fetching summary: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/suggestions")
def get_suggestions():
    if not ensure_db_exists():
        return jsonify({"success": False, "error": "Database not initialized"}), 500

    try:
        conn = get_db()
        cur = conn.cursor()

        query = request.args.get("q", "").strip()
        suggestions = []

        if query:
            # Use LIKE for partial matching, case-insensitive
            cur.execute("SELECT DISTINCT person FROM transactions WHERE person IS NOT NULL AND person != '' AND person LIKE ? LIMIT 10", (f"%{query}%",))
            suggestions = [row['person'] for row in cur.fetchall()]

        conn.close()

        return jsonify({"success": True, "suggestions": suggestions})
    except Exception as e:
        print(f"Error fetching suggestions: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    if ensure_db_exists():
        if not os.path.exists(DB_FILE) or os.path.getsize(DB_FILE) == 0:
            if process_xml():
                print("Application started successfully")
            else:
                print("Error: Failed to process XML data")
        else:
            print("Application started successfully")
    else:
        print("Error: Failed to initialize database")
    
    app.run(debug=True)
