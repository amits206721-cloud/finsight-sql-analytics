# 💰 FinSight: SQL & DQL Analytics Dashboard

> A lightweight, full-stack financial analytics web application built with Python (Flask) and SQLite, designed to demonstrate advanced Data Query Language (DQL) reporting, database normalization principles, and real-time data aggregation.

---

## 🚀 Key Features
* **Interactive Dashboard:** View real-time category summaries and recent transactions updated directly from the database.
* **Dynamic Expense Insertion:** Submit new financial transactions via a web form that executes secure parameterized SQL `INSERT` commands.
* **Database-Level Aggregations:** Leverages SQL clauses (`GROUP BY`, `SUM`, `ORDER BY`) to process calculations at the database engine level rather than relying on application-layer loops.
* **Clean Modern UI:** Styled using Bootstrap 5 for responsive presentation across devices.

---

## 🛠️ Tech Stack
* **Backend:** Python, Flask
* **Database Engine:** SQLite
* **Frontend:** HTML5, CSS3, Bootstrap 5
* **Version Control:** Git & GitHub

---

## 📊 Core DQL Queries Powering the Application

### 1. Category-Wise Spending Summary (`GROUP BY` + `SUM`)
Used on the main dashboard to compute total expenditures grouped by expense category, sorted in descending order:
```sql
SELECT category, SUM(amount) AS total_spent 
FROM expenses 
GROUP BY category 
ORDER BY total_spent DESC;
```

### 2. Transaction Retrieval & Ordering (`SELECT` + `ORDER BY`)
Fetches and displays recent transactions sorted by date:
```sql
SELECT * 
FROM expenses 
ORDER BY spend_date DESC;
```

---

## ⚙️ How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/finsight-sql-analytics.git
   cd finsight-sql-analytics
   ```

2. **Install dependencies:**
   ```bash
   pip install flask
   ```

3. **Initialize the database:**
   Run the setup script to create the SQLite database and seed initial sample data:
   ```bash
   python step1_db.py
   ```

4. **Run the Flask web application:**
   ```bash
   python app.py
   ```
   The app uses the `finsight.db` file next to `app.py` and creates the expenses table if needed, so it can also run without first running the seed script. The seed script is safe to rerun and does not delete existing transactions.

5. **Open your browser:**
   Navigate to `http://127.0.0.1:5000` to interact with your dashboard.

---

## 📁 Project Structure
```text
finsight/
├── finsight.db             # SQLite database file
├── app.py                  # Flask routes, database access, and CSV export
├── step1_db.py             # Safe database initialization and optional sample data
├── step2_groupby.py        # Standalone SQL aggregation examples
├── README.md               # Project documentation
└── templates/
    ├── base.html            # Shared layout and application navigation
    ├── index.html           # Dashboard and quick expense entry
    ├── transactions.html    # Searchable transaction ledger
    ├── analytics.html       # Spending analytics
    ├── categories.html      # Category summaries
    ├── reports.html         # CSV export and report summary
    ├── trash.html           # Deleted transaction recovery
    └── settings.html        # Application settings
```