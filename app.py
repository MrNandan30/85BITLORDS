from flask import Flask, render_template, request, send_file, session, jsonify, g
import os
import sqlite3
import uuid
import datetime
import pandas as pd

from extractor import extract_data_from_file, auto_categorize
from excel_writer import save_to_excel
from utils import extract_year, extract_month

from db_utils import (
    init_db, insert_bill, get_bills_by_category, insert_category,
    delete_category, delete_bill, get_all_categories,
    get_db_connection
)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'

app = Flask(__name__)
app.secret_key = 'super-secret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

init_db()  # ✅ Initialize DB once


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files[]' not in request.files:
        return "No files uploaded", 400

    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    files = request.files.getlist('files[]')

    for f in files:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
        f.save(filepath)

        # Extract and structure data
        data = extract_data_from_file(filepath)
        required_fields = ['date', 'amount', 'provider']
        missing_fields = [field for field in required_fields if not getattr(data, field)]

        if missing_fields:
            return jsonify({
                'filename': f.filename,
                'missing_fields': missing_fields
            }), 206

        data_dict = {
            'filename': f.filename,
            'date': data.date,
            'amount': float(data.amount) if data.amount != "-" else 0.0,
            'provider': data.provider,
            'category': auto_categorize(data),
            'year': extract_year(data.date),
            'month': extract_month(data.date),
            'needs_review': data.needs_review
        }

        insert_bill(data_dict)

    return '', 204


@app.route('/download/<category>')
def download_excel(category):
    bills = get_bills_by_category(category if category.lower() != 'misc' else None)
    if not bills:
        return "No data to download", 404

    df = pd.DataFrame(bills, columns=[
        "id", "filename", "date", "amount", "provider",
        "category", "year", "month", "needs_review"
    ])
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{category}_bills_{timestamp}.xlsx"
    filepath = os.path.join(OUTPUT_FOLDER, filename)
    df.to_excel(filepath, index=False)
    return send_file(filepath, as_attachment=True)


@app.route('/category/<category>')
def view_category(category):
    bills = get_bills_by_category(None if category.lower() == 'misc' else category)
    categories = get_all_categories()
    return render_template('category_view.html', category=category, bills=bills, categories=categories)


@app.route('/add_category', methods=['POST'])
def add_category():
    data = request.get_json()
    category = data.get('category', '').strip().lower()
    if not category:
        return jsonify(success=False)
    insert_category(category)
    return jsonify(success=True)


@app.route('/delete_category/<name>', methods=['POST'])
def delete_category_route(name):
    delete_category(name)
    return '', 204


@app.route('/delete_bill/<int:bill_id>', methods=['POST'])
def delete_bill_route(bill_id):
    delete_bill(bill_id)
    return '', 204


@app.route('/manual_field_prompt', methods=['POST'])
def manual_field_prompt():
    req = request.get_json()
    missing = req.get('missing', [])

    conn = get_db_connection()
    cursor = conn.cursor()

    suggestions = {}
    for field in missing:
        try:
            cursor.execute(f"""
                SELECT DISTINCT {field}
                FROM bills
                WHERE {field} IS NOT NULL
                ORDER BY ROWID DESC
                LIMIT 10
            """)
            results = cursor.fetchall()
            suggestions[field] = [row[0] for row in results if row[0] is not None]
        except Exception:
            suggestions[field] = []

    conn.close()
    return jsonify({'suggestions': suggestions})


@app.route('/manual_field_submit', methods=['POST'])
def manual_field_submit():
    req = request.get_json()
    filename = req['filename']
    fields = req['fields']

    conn = get_db_connection()
    cursor = conn.cursor()

    update_fields = ', '.join([f"{k} = ?" for k in fields.keys()])
    values = list(fields.values()) + [filename]

    try:
        cursor.execute(f"UPDATE bills SET {update_fields}, needs_review = 0 WHERE filename = ?", values)
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        print("Error saving manual entry:", e)
        return jsonify({'success': False, 'error': str(e)})


@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()


if __name__ == '__main__':
    init_db()
    app.run(debug=True)