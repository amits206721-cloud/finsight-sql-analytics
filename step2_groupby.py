import sqlite3

# 1. Connect to our existing database
conn = sqlite3.connect("finsight.db")
cursor = conn.cursor()

print("--- DQL 4: Total Spending by Category (GROUP BY + SUM) ---")
# This groups your rows by category and adds up all amounts
cursor.execute("""
SELECT category, SUM(amount) AS total_spent
FROM expenses
GROUP BY category
ORDER BY total_spent DESC
""")
for row in cursor.fetchall():
    # row[0] is category, row[1] is total_spent
    print(f"Category: {row[0]:<15} | Total Spent: ₹{row[1]}")

print("\n--- DQL 5: How Many Times You Paid via UPI vs Card (GROUP BY + COUNT) ---")
cursor.execute("""
SELECT payment_mode, COUNT(*) AS transaction_count, SUM(amount) AS total_amount
FROM expenses
GROUP BY payment_mode
""")
for row in cursor.fetchall():
    print(f"Mode: {row[0]:<10} | Transactions: {row[1]} | Total: ₹{row[2]}")

print("\n--- DQL 6: Categories Where Total Spend is Greater than ₹500 (HAVING clause) ---")
cursor.execute("""
SELECT category, SUM(amount) AS total_spent
FROM expenses
GROUP BY category
HAVING total_spent > 500
ORDER BY total_spent DESC
""")
for row in cursor.fetchall():
    print(f"Category: {row[0]:<15} | Spent: ₹{row[1]}")

conn.close()