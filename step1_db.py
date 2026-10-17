import sqlite3
from pathlib import Path

# 1. Connect to the project database regardless of the current working directory
conn = sqlite3.connect(Path(__file__).with_name("finsight.db"))
cursor = conn.cursor()

# 2. Create ONE simple table
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    payment_mode TEXT NOT NULL,
    amount INTEGER NOT NULL,
    spend_date TEXT NOT NULL
)
""")

# 3. Seed sample transactions only when the database is empty.
sample_data = [
    ("Zomato Dinner", "Food", "UPI", 350, "2026-10-01"),
    ("Monthly Metro Pass", "Travel", "UPI", 600, "2026-10-02"),
    ("Amazon Headphones", "Shopping", "Card", 1800, "2026-10-05"),
    ("Swiggy Snacks", "Food", "UPI", 180, "2026-10-06"),
    ("Jio Mobile Recharge", "Bills", "UPI", 299, "2026-10-08"),
    ("Uber Auto", "Travel", "UPI", 120, "2026-10-10"),
    ("Electricity Bill", "Bills", "NetBanking", 1450, "2026-10-12"),
    ("BookMyShow Movie", "Entertainment", "Card", 450, "2026-10-14")
]

if cursor.execute("SELECT COUNT(*) FROM expenses").fetchone()[0] == 0:
    cursor.executemany("""
    INSERT INTO expenses (title, category, payment_mode, amount, spend_date)
    VALUES (?, ?, ?, ?, ?)
    """, sample_data)

conn.commit()
print("Database initialized. Existing transactions were preserved.\n")

# ==========================================
# NOW LET'S RUN 3 BASIC DQL (SELECT) QUERIES
# ==========================================

print("--- DQL 1: View All Expenses (SELECT *) ---")
cursor.execute("SELECT * FROM expenses")
for row in cursor.fetchall():
    print(row)

print("\n--- DQL 2: Filter Only UPI Payments Over INR 200 (WHERE + AND) ---")
cursor.execute("""
SELECT title, amount, spend_date 
FROM expenses 
WHERE payment_mode = 'UPI' AND amount > 200
""")
for row in cursor.fetchall():
    print(row)

print("\n--- DQL 3: Top 3 Most Expensive Purchases (ORDER BY + LIMIT) ---")
cursor.execute("""
SELECT title, category, amount 
FROM expenses 
ORDER BY amount DESC 
LIMIT 3
""")
for row in cursor.fetchall():
    print(row)

conn.close()