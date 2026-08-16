"""
Smart Finance Insights - Database Initialization
Creates all tables and seeds sample data for demonstration.
Run: python init_db.py
"""
import sqlite3
import os
from datetime import datetime, timedelta
from utils.helpers import hash_password

DB_PATH = os.path.join(os.path.dirname(__file__), 'finance.db')


def get_db_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables():
    """Create all database tables."""
    conn = get_db_conn()
    cur = conn.cursor()

    # ---------- USERS ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT,
        occupation TEXT,
        monthly_income REAL DEFAULT 0,
        age INTEGER,
        created_at TEXT DEFAULT (datetime('now','localtime'))
    )
    """)

    # ---------- INCOME ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS income (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        source TEXT NOT NULL,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        notes TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # ---------- EXPENSES ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        description TEXT,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # ---------- BUDGETS ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        month INTEGER NOT NULL,
        year INTEGER NOT NULL,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # ---------- INVESTMENTS ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS investments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        asset_type TEXT NOT NULL,
        investment_name TEXT NOT NULL,
        invested_amount REAL NOT NULL,
        current_value REAL NOT NULL,
        purchase_date TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # ---------- GOALS ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        goal_name TEXT NOT NULL,
        target_amount REAL NOT NULL,
        saved_amount REAL DEFAULT 0,
        target_date TEXT,
        category TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # ---------- NOTIFICATIONS ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        message TEXT NOT NULL,
        priority TEXT DEFAULT 'Medium',
        status TEXT DEFAULT 'Active',
        created_at TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # ---------- BILLS ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        bill_name TEXT NOT NULL,
        amount REAL NOT NULL,
        due_date TEXT NOT NULL,
        category TEXT,
        status TEXT DEFAULT 'Pending',
        created_at TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    # ---------- JARVIS CHAT HISTORY ----------
    cur.execute("""
    CREATE TABLE IF NOT EXISTS jarvis_chat (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()
    print("[OK] All tables created successfully.")


def seed_sample_data():
    """Insert a demo user with comprehensive sample data."""
    conn = get_db_conn()
    cur = conn.cursor()

    # Check if demo user exists
    cur.execute("SELECT id FROM users WHERE email = ?", ('demo@smartfinance.com',))
    existing = cur.fetchone()
    if existing:
        conn.close()
        print("[OK] Sample data already exists. Skipping seed.")
        return

    # Create demo user
    cur.execute("""
        INSERT INTO users (name, email, password, phone, occupation, monthly_income, age)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('John Doe', 'demo@smartfinance.com', hash_password('demo123'),
          '9876543210', 'Software Engineer', 80000, 30))
    user_id = cur.lastrowid

    today = datetime.now()
    current_month = today.month
    current_year = today.year

    # ---------- INCOME (last 6 months) ----------
    income_sources = [
        ('Salary', 80000), ('Freelance', 15000), ('Dividend', 3500),
        ('Rental', 12000), ('Bonus', 5000)
    ]
    for m_offset in range(6):
        m = current_month - m_offset
        y = current_year
        if m <= 0:
            m += 12
            y -= 1
        day = 1 if m_offset > 0 else today.day
        for src, amt in income_sources[:3]:
            date_str = f"{y}-{m:02d}-{day:02d}"
            cur.execute("""
                INSERT INTO income (user_id, source, amount, date, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, src, amt, date_str, f'Monthly {src}'))

    # ---------- EXPENSES (last 6 months, varied categories) ----------
    expense_categories = {
        'Food': [350, 420, 380, 510, 450, 390, 410, 480, 350, 420, 380, 510, 450, 390, 410, 480, 350, 420, 380, 510],
        'Shopping': [800, 1200, 500, 2000, 3500, 900, 1500, 2200, 800, 1200, 500, 2000, 3500, 900, 1500, 2200],
        'Bills': [2500, 3200, 2800, 4100, 3500, 2900, 3100, 3800, 2500, 3200, 2800, 4100, 3500, 2900, 3100, 3800],
        'Entertainment': [300, 500, 200, 800, 600, 400, 350, 700, 300, 500, 200, 800, 600, 400, 350, 700],
        'Transport': [200, 350, 280, 400, 320, 250, 380, 420, 200, 350, 280, 400, 320, 250, 380, 420],
        'Health': [500, 800, 200, 1200, 600, 300, 900, 400, 500, 800, 200, 1200, 600, 300, 900, 400],
    }
    descriptions = {
        'Food': ['Grocery', 'Restaurant', 'Food Delivery', 'Snacks'],
        'Shopping': ['Clothes', 'Electronics', 'Home Goods', 'Online Order'],
        'Bills': ['Electricity', 'Water', 'Internet', 'Mobile', 'Gas'],
        'Entertainment': ['Movie', 'Subscription', 'Game', 'Concert'],
        'Transport': ['Fuel', 'Uber', 'Metro', 'Parking'],
        'Health': ['Pharmacy', 'Doctor Visit', 'Gym', 'Supplements'],
    }

    for m_offset in range(6):
        m = current_month - m_offset
        y = current_year
        if m <= 0:
            m += 12
            y -= 1
        days_in_month = 28
        for cat, amounts in expense_categories.items():
            for i, amt in enumerate(amounts):
                if i >= days_in_month:
                    break
                day = i + 1
                date_str = f"{y}-{m:02d}-{day:02d}"
                desc = descriptions[cat][i % len(descriptions[cat])]
                cur.execute("""
                    INSERT INTO expenses (user_id, category, description, amount, date)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, cat, desc, amt, date_str))

    # ---------- BUDGETS (current month) ----------
    budget_data = [
        ('Food', 12000), ('Shopping', 8000), ('Bills', 15000),
        ('Entertainment', 6000), ('Transport', 5000), ('Health', 4000)
    ]
    for cat, amt in budget_data:
        cur.execute("""
            INSERT INTO budgets (user_id, category, amount, month, year)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, cat, amt, current_month, current_year))

    # ---------- INVESTMENTS ----------
    investments = [
        ('Stocks', 'Tata Motors', 100000, 125000),
        ('Stocks', 'Reliance Industries', 85000, 98000),
        ('Mutual Funds', 'Axis Bluechip Fund', 50000, 58500),
        ('Mutual Funds', 'SBI Small Cap Fund', 40000, 47800),
        ('Gold', 'Gold ETF', 30000, 34500),
        ('Fixed Deposits', 'HDFC FD - 5 Year', 100000, 112000),
        ('Bonds', 'Government Bond 7.1%', 50000, 53500),
        ('Real Estate', 'Residential Plot', 200000, 250000),
    ]
    for asset, name, invested, current in investments:
        purchase_date = (today - timedelta(days=180)).strftime('%Y-%m-%d')
        cur.execute("""
            INSERT INTO investments (user_id, asset_type, investment_name, invested_amount, current_value, purchase_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, asset, name, invested, current, purchase_date))

    # ---------- GOALS ----------
    goals = [
        ('Emergency Fund', 200000, 150000, '2026-12-31', 'Savings'),
        ('Vacation Savings', 80000, 32000, '2026-10-15', 'Travel'),
        ('Home Purchase', 1500000, 450000, '2028-06-30', 'Property'),
        ('Vehicle Purchase', 500000, 240000, '2027-03-31', 'Vehicle'),
        ('Retirement Fund', 5000000, 850000, '2045-12-31', 'Retirement'),
        ('Education Fund', 300000, 75000, '2028-05-31', 'Education'),
    ]
    for name, target, saved, date, cat in goals:
        cur.execute("""
            INSERT INTO goals (user_id, goal_name, target_amount, saved_amount, target_date, category)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, name, target, saved, date, cat))

    # ---------- BILLS ----------
    bills = [
        ('Electricity Bill', 2500, (today + timedelta(days=5)).strftime('%Y-%m-%d'), 'Bills'),
        ('Internet Bill', 1200, (today + timedelta(days=10)).strftime('%Y-%m-%d'), 'Bills'),
        ('Credit Card Payment', 8500, (today + timedelta(days=15)).strftime('%Y-%m-%d'), 'Bills'),
        ('Mobile Recharge', 499, (today + timedelta(days=3)).strftime('%Y-%m-%d'), 'Bills'),
        ('Insurance Premium', 12000, (today + timedelta(days=20)).strftime('%Y-%m-%d'), 'Insurance'),
    ]
    for name, amt, due, cat in bills:
        cur.execute("""
            INSERT INTO bills (user_id, bill_name, amount, due_date, category)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, name, amt, due, cat))

    # ---------- NOTIFICATIONS ----------
    notifications = [
        ('Budget Alert', 'Food expenses exceeded budget by ₹2,000 this month', 'High', 'Active'),
        ('Bill Reminder', f'Electricity bill due on {(today + timedelta(days=5)).strftime("%d-%b-%Y")}', 'Medium', 'Pending'),
        ('Savings Goal', 'Save ₹5,000 more this month to reach your Emergency Fund goal', 'Medium', 'Active'),
        ('Investment Alert', 'Mutual Fund portfolio increased by 4.2% this month', 'Low', 'Completed'),
        ('Low Balance', 'Consider increasing your emergency fund for better coverage', 'High', 'Active'),
        ('Goal Milestone', 'Emergency Fund reached 75% completion!', 'Medium', 'Completed'),
    ]
    for ntype, msg, prio, status in notifications:
        cur.execute("""
            INSERT INTO notifications (user_id, type, message, priority, status)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, ntype, msg, prio, status))

    conn.commit()
    conn.close()
    print("[OK] Sample data inserted for demo user (demo@smartfinance.com / demo123).")


def main():
    print("=" * 60)
    print("  Smart Finance Insights - Database Initialization")
    print("=" * 60)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("[INFO] Existing database removed.")
    create_tables()
    seed_sample_data()
    print("=" * 60)
    print("  Database ready! Run: python app.py")
    print("  Login: demo@smartfinance.com / demo123")
    print("=" * 60)


if __name__ == '__main__':
    main()
