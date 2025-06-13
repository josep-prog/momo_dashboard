from flask import Flask, jsonify, request, send_from_directory
import sqlite3
from db import get_unique_names
import traceback
import os
app = Flask(__name__)
DB_PATH = 'corrected_data.db'

def get_db():
    try:
        if not os.path.exists(DB_PATH):
            raise FileNotFoundError(f"Database file {DB_PATH} not found. Please run process.py first.")
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")
        raise

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)