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

@app.route('/data')
def get_data():
    try:
        tx_type = request.args.get('type', 'all')
        name = request.args.get('name', 'all')
        
        print(f"Processing request - Type: {tx_type}, Name: {name}")
        
        conn = get_db()
        if not conn:
            raise Exception("Could not connect to database")

        # Base query for transactions with proper filter combinations
        query = """
            WITH filtered_transactions AS (
                SELECT 
                    type,
                    amount,
                    date,
                    body,
                    address,
                    readable_date,
                    name,
                    COUNT(*) OVER() as total_count,
                    SUM(amount) OVER() as total_amount
                FROM transactions 
                WHERE 1=1
        """
        params = []

        if tx_type != 'all':
            query += " AND type = ?"
            params.append(tx_type)
        
        if name != 'all':
            query += " AND name LIKE ? COLLATE NOCASE"
            params.append(f"%{name}%")

        query += """
            )
            SELECT * FROM filtered_transactions
            ORDER BY date DESC
        """

        print(f"Executing query: {query} with params: {params}")
        
        try:
            transactions = conn.execute(query, params).fetchall()
            transactions = [dict(tx) for tx in transactions]
        except sqlite3.Error as e:
            print(f"Database error: {str(e)}")
            raise

        # Get chart data based on filtered transactions
        chart_query = """
            WITH filtered_transactions AS (
                SELECT type, amount
                FROM transactions
                WHERE 1=1
        """
        if tx_type != 'all':
            chart_query += " AND type = ?"
        if name != 'all':
            chart_query += " AND name LIKE ? COLLATE NOCASE"
        
        chart_query += """
            )
            SELECT 
                type, 
                COUNT(*) as count,
                SUM(amount) as total_amount
            FROM filtered_transactions
            GROUP BY type 
            ORDER BY count DESC
        """
        
        try:
            chart = conn.execute(chart_query, params).fetchall()
        except sqlite3.Error as e:
            print(f"Chart query error: {str(e)}")
            raise

        labels = [row['type'] for row in chart]
        values = [row['count'] for row in chart]
        amounts = [row['total_amount'] for row in chart]

        # Get unique names from the database
        try:
            names = get_unique_names()
        except Exception as e:
            print(f"Error getting unique names: {str(e)}")
            names = []

        # Calculate totals
        total_count = transactions[0]['total_count'] if transactions else 0
        total_amount = transactions[0]['total_amount'] if transactions else 0

        response_data = {
            'transactions': transactions,
            'chart_data': {
                'labels': labels,
                'values': values,
                'amounts': amounts
            },
            'total_count': total_count,
            'total_amount': total_amount,
            'names': names
        }

        print(f"Successfully processed request. Found {total_count} transactions.")
        return jsonify(response_data)

    except Exception as e:
        error_msg = f"Error in get_data: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'error': str(e), 'details': error_msg}), 500

if __name__ == '__main__':
    app.run(debug=True)