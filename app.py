from flask import Flask, render_template, request, jsonify
import xml.etree.ElementTree as ET
import sqlite3
import re
import os

app = Flask(__name__)

DB_FILE = "momo.db"
XML_FILE = "data.xml"

# Parse, clean, and insert data into DB
def process_xml():
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

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    with open("schema.sql") as f:
        cur.executescript(f.read())

    for sms in root.findall("sms"):
        body = sms.get("body").lower()
        date = sms.get("readable_date")
        for t, pattern in categories.items():
            if re.search(pattern, body):
                amount_match = re.search(r"(\d{3,}) rwf", body)
                person_match = re.search(r"from (.*?)\(|to (.*?)\d{2,}", body)
                amount = int(amount_match.group(1)) if amount_match else 0
                person = person_match.group(1) if person_match else "unknown"
                cur.execute('''
                    INSERT INTO transactions (type, amount, person, date, raw_sms)
                    VALUES (?, ?, ?, ?, ?)
                ''', (t, amount, person.strip(), date, body))
                break
    conn.commit()
    conn.close()

@app.route("/")
def dashboard():
    return render_template("index.html")

@app.route("/api/data")
def data():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    q = request.args.get("q", "")
    if q:
        cur.execute("SELECT * FROM transactions WHERE type LIKE ? OR person LIKE ?", (f"%{q}%", f"%{q}%"))
    else:
        cur.execute("SELECT * FROM transactions")
    data = [dict(id=row[0], type=row[1], amount=row[2], person=row[3], date=row[4], raw_sms=row[5]) for row in cur.fetchall()]
    conn.close()
    return jsonify(data)

if __name__ == "__main__":
    if not os.path.exists(DB_FILE):
        process_xml()
    app.run(debug=True)
