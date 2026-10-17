import csv
import io
import sqlite3
from datetime import date
from pathlib import Path

from flask import Flask, abort, make_response, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = 'finsight_secret_key_demo'
DATABASE_PATH = Path(__file__).with_name('finsight.db')


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            payment_mode TEXT NOT NULL,
            amount INTEGER NOT NULL,
            spend_date TEXT NOT NULL
        )
    ''')
    return conn


@app.context_processor
def inject_trash_count():
    return {'trash_count': len(session.get('deleted_items', []))}


@app.route('/')
def index():
    conn = get_db_connection()
    category_summary = conn.execute('''
        SELECT category, SUM(amount) AS total_spent
        FROM expenses
        GROUP BY category
        ORDER BY total_spent DESC
    ''').fetchall()
    expenses = conn.execute(
        'SELECT * FROM expenses ORDER BY spend_date DESC, id DESC'
    ).fetchall()
    conn.close()

    return render_template(
        'index.html',
        category_summary=category_summary,
        expenses=expenses,
        today=date.today().isoformat()
    )


@app.route('/add', methods=['POST'])
def add_expense():
    title = request.form.get('title', '').strip()
    category = request.form.get('category', '').strip()
    payment_mode = request.form.get('payment_mode', '').strip()
    amount_value = request.form.get('amount', '').strip()
    spend_date = request.form.get('spend_date', '').strip()

    try:
        amount = int(amount_value)
        date.fromisoformat(spend_date)
    except ValueError:
        abort(400, description='Enter a whole-number amount and a valid date.')

    if not title or not category or not payment_mode or amount <= 0:
        abort(400, description='Complete every field and enter an amount greater than zero.')

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
        deleted_items = session.get('deleted_items', [])
        deleted_items.insert(0, {
            'title': item['title'],
            'category': item['category'],
            'payment_mode': item['payment_mode'],
            'amount': item['amount'],
            'spend_date': item['spend_date']
        })
        session['deleted_items'] = deleted_items

    conn.execute('DELETE FROM expenses WHERE id = ?', (txn_id,))
    conn.commit()
    conn.close()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.accept_mimetypes:
        return {'status': 'success', 'trash_count': len(session.get('deleted_items', []))}

    # Fixed redirect: Go back to the page the user clicked delete from
    return redirect(request.referrer or url_for('index'))


@app.route('/transactions')
def transactions():
    conn = get_db_connection()
    expenses = conn.execute(
        'SELECT * FROM expenses ORDER BY spend_date DESC, id DESC'
    ).fetchall()
    conn.close()
    return render_template('transactions.html', expenses=expenses)


@app.route('/analytics')
def analytics():
    conn = get_db_connection()
    total_spend = conn.execute(
        'SELECT COALESCE(SUM(amount), 0) FROM expenses'
    ).fetchone()[0]
    top_cat = conn.execute('''
        SELECT category, SUM(amount) AS total
        FROM expenses
        GROUP BY category
        ORDER BY total DESC, category
        LIMIT 1
    ''').fetchone()
    mode_summary = conn.execute('''
        SELECT payment_mode, SUM(amount) AS total
        FROM expenses
        GROUP BY payment_mode
        ORDER BY total DESC, payment_mode
    ''').fetchall()
    conn.close()
    return render_template(
        'analytics.html',
        total_spend=total_spend,
        top_cat=top_cat,
        mode_summary=mode_summary
    )


@app.route('/categories')
def categories():
    conn = get_db_connection()
    category_summary = conn.execute('''
        SELECT category, COUNT(*) AS count, SUM(amount) AS total_spent
        FROM expenses
        GROUP BY category
        ORDER BY total_spent DESC, category
    ''').fetchall()
    conn.close()
    return render_template('categories.html', category_summary=category_summary)


@app.route('/reports')
def reports():
    conn = get_db_connection()
    expenses = conn.execute(
        'SELECT * FROM expenses ORDER BY spend_date DESC, id DESC'
    ).fetchall()
    total_spend = conn.execute(
        'SELECT COALESCE(SUM(amount), 0) FROM expenses'
    ).fetchone()[0]
    conn.close()
    return render_template('reports.html', expenses=expenses, total_spend=total_spend)


@app.route('/export.csv')
def export_csv():
    conn = get_db_connection()
    expenses = conn.execute(
        'SELECT id, title, category, payment_mode, amount, spend_date '
        'FROM expenses ORDER BY spend_date DESC, id DESC'
    ).fetchall()
    conn.close()

    output = io.StringIO(newline='')
    writer = csv.writer(output)
    writer.writerow(('ID', 'Title', 'Category', 'Payment Mode', 'Amount', 'Date'))
    writer.writerows(tuple(expense) for expense in expenses)

    response = make_response(output.getvalue())
    response.mimetype = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=expenses.csv'
    return response


@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/trash')
def trash():
    deleted_items = session.get('deleted_items', [])
    return render_template('trash.html', deleted_items=deleted_items)


@app.route('/restore/<int:index>')
def restore_item(index):
    deleted_items = session.get('deleted_items', [])
    if 0 <= index < len(deleted_items):
        item = deleted_items.pop(index)
        session['deleted_items'] = deleted_items

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO expenses (title, category, payment_mode, amount, spend_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (item['title'], item['category'], item['payment_mode'], item['amount'], item['spend_date']))
        conn.commit()
        conn.close()

    return redirect(url_for('trash'))


@app.route('/trash/delete/<int:index>')
def trash_delete(index):
    deleted_items = session.get('deleted_items', [])
    if 0 <= index < len(deleted_items):
        deleted_items.pop(index)
        session['deleted_items'] = deleted_items
    return redirect(url_for('trash'))


@app.route('/trash/empty')
def empty_trash():
    session.pop('deleted_items', None)
    return redirect(url_for('trash'))


if __name__ == '__main__':
    app.run(debug=True)