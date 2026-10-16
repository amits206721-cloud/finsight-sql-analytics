from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import date

app = Flask(__name__)
app.secret_key = 'finsight_secret_key_demo'

def get_db_connection():
    conn = sqlite3.connect('finsight.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    
    category_summary = conn.execute('''
        SELECT category, SUM(amount) AS total_spent 
        FROM expenses 
        GROUP BY category 
        ORDER BY total_spent DESC
    ''').fetchall()
    
    expenses = conn.execute('SELECT * FROM expenses ORDER BY spend_date DESC').fetchall()
    conn.close()
    
    trash_count = len(session.get('deleted_items', []))
    return render_template(
        'index.html',
        category_summary=category_summary,
        expenses=expenses,
        trash_count=trash_count,
        today=date.today().isoformat()
    )

@app.route('/add', methods=['POST'])
def add_expense():
    title = request.form['title']
    category = request.form['category']
    payment_mode = request.form['payment_mode']
    amount = request.form['amount']
    spend_date = request.form['spend_date']
    
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO expenses (title, category, payment_mode, amount, spend_date)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, category, payment_mode, amount, spend_date))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

@app.route('/delete/<int:txn_id>')
def delete_expense(txn_id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM expenses WHERE id = ?', (txn_id,)).fetchone()
    
    if item:
        if 'deleted_items' not in session:
            session['deleted_items'] = []
            
        deleted_item = {
            'title': item['title'],
            'category': item['category'],
            'payment_mode': item['payment_mode'],
            'amount': item['amount'],
            'spend_date': item['spend_date']
        }
        session['deleted_items'].insert(0, deleted_item)
        session.modified = True
    
    conn.execute('DELETE FROM expenses WHERE id = ?', (txn_id,))
    conn.commit()
    conn.close()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.accept_mimetypes:
        trash_count = len(session.get('deleted_items', []))
        return {'status': 'success', 'trash_count': trash_count}
        
    return redirect(url_for('index'))

@app.route('/trash')
def trash():
    deleted_items = session.get('deleted_items', [])
    trash_count = len(deleted_items)
    return render_template('trash.html', deleted_items=deleted_items, trash_count=trash_count)

@app.route('/restore/<int:index>')
def restore_item(index):
    deleted_items = session.get('deleted_items', [])
    if 0 <= index < len(deleted_items):
        item = deleted_items.pop(index)
        session.modified = True
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO expenses (title, category, payment_mode, amount, spend_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (item['title'], item['category'], item['payment_mode'], item['amount'], item['spend_date']))
        conn.commit()
        conn.close()
        
    return redirect(url_for('trash'))

if __name__ == '__main__':
    app.run(debug=True)