# Smart Finance Insights

A complete, production-ready **personal finance management dashboard** built with **Python Flask** + **SQLite** + **Jinja2** templates. This project combines ALL features from 4 milestones into a single, fully-functional web application.

![Smart Finance Dashboard](https://img.shields.io/badge/SmartFinance-Insights-16a34a) ![Python](https://img.shields.io/badge/Python-3.8+-blue) ![Flask](https://img.shields.io/badge/Flask-3.x-green)

---

## 📋 Table of Contents
1. [Overview](#overview)
2. [Features (All 4 Milestones)](#features)
3. [Technology Stack](#technology-stack)
4. [Installation & Setup](#installation--setup)
5. [Demo Login](#demo-login)
6. [Project Structure](#project-structure)
7. [Module Documentation](#module-documentation)
8. [API Endpoints](#api-endpoints)
9. [Screenshots & Sample Outputs](#screenshots)

---

## Overview

**Smart Finance Insights** is a web application that helps users manage their personal finances by recording income/expenses, creating budgets, tracking investments & goals, viewing AI-powered insights, and generating financial reports — all in one beautiful dashboard.

---

## Features

### 🟢 Milestone 1 — Core Finance Management
| Feature | Description |
|---------|-------------|
| **User Authentication** | Registration, Login, Logout with password hashing (SHA-256 + salt) |
| **Profile Management** | View/edit profile, change password |
| **Expense Tracking** | Add/Edit/Delete income & expenses with categorization |
| **Categories** | Food, Shopping, Bills, Entertainment, Transport, Health, Education, Other |
| **Budget Planning** | Create monthly budgets per category, track utilization, progress bars |
| **Financial Dashboard** | Summary cards (Income, Expense, Savings, Investment), charts, recent transactions |
| **Transaction History** | Filterable by type, category, month, year |
| **AI Spending Analysis** | Expense percentage, basic suggestions |

### 🔵 Milestone 2 — Investment Tracking & Goal Planning
| Feature | Description |
|---------|-------------|
| **Investment Portfolio** | Add/Edit/Delete investments (Stocks, Mutual Funds, Gold, FD, Bonds, Real Estate, Crypto) |
| **Profit/Loss Calculation** | Automatic P/L and Return on Investment (ROI) per investment |
| **Asset Allocation** | Visual pie chart of portfolio distribution |
| **Portfolio Analytics Dashboard** | Total invested, current value, growth charts, risk analysis |
| **Top/Low Performers** | Identify best and worst performing assets |
| **Financial Goal Planning** | Create goals (Emergency Fund, Vacation, Home, Retirement, etc.) |
| **Goal Progress Tracking** | Completion %, remaining amount, days left, status (On Track/Behind/Achieved) |
| **Goal Contributions** | Add savings contributions to any goal |

### 🟣 Milestone 3 — Intelligence & Insights
| Feature | Description |
|---------|-------------|
| **Spending Pattern Analysis** | Category-wise breakdown, monthly trends, high-spending detection |
| **Budget Recommendations** | AI-generated personalized budget suggestions based on spending history |
| **Financial Health Score** | 0-100 score with status (Excellent/Good/Fair/Poor) |
| **Health Indicators** | Savings Ratio, Expense Ratio, Investment Growth, Debt-to-Income, Emergency Fund coverage |
| **Alert & Notification System** | Auto-generated alerts: budget exceeded, bill reminders, goal milestones, investment updates, low balance |
| **AI-Based Financial Insights** | Personalized recommendations: savings tips, investment suggestions, spending warnings |
| **Intelligence Dashboard** | Combined view of all analytics, recommendations, score, and notifications |

### 🟠 Milestone 4 — Reporting & Finalization
| Feature | Description |
|---------|-------------|
| **Advanced Financial Reports** | 4 report types: Monthly Expense, Budget Utilization, Investment Performance, Goal Progress |
| **PDF Export** | Download any report as a professionally formatted PDF |
| **Excel Export** | Download any report as a styled Excel (.xlsx) spreadsheet |
| **Dashboard Optimization** | Optimized SQL queries, efficient data loading, summary cards |
| **JARVIS AI Assistant** | Interactive chatbot that answers finance queries in natural language |
| **JARVIS Capabilities** | Expense summary, budget recommendations, investment analysis, goal tracking, health score, financial insights |
| **Security** | Password hashing, input validation, session management, SQL injection prevention (parameterized queries) |

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.8+ / Flask 3.x |
| **Database** | SQLite (via Python's `sqlite3` module) |
| **Templating** | Jinja2 (Flask built-in) |
| **Frontend** | HTML5, CSS3, JavaScript (vanilla) |
| **Charts** | Chart.js v4 (CDN) |
| **Icons** | Bootstrap Icons (CDN) |
| **Fonts** | Google Fonts - Inter (CDN) |
| **PDF Export** | fpdf2 |
| **Excel Export** | openpyxl |

---

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Extract/Download** the project folder:
   ```bash
   cd smart-finance-insights
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize the database** (creates tables + sample data):
   ```bash
   python init_db.py
   ```
   This creates `finance.db` with a demo user and comprehensive sample data (6 months of transactions, budgets, investments, goals, notifications).

4. **Start the application**:
   ```bash
   python app.py
   ```

5. **Open in browser**:
   ```
   http://localhost:5000
   ```

---

## Demo Login

| Field | Value |
|-------|-------|
| **Email** | `demo@smartfinance.com` |
| **Password** | `demo123` |

The demo account comes pre-loaded with:
- 6 months of income & expense transactions
- Monthly budgets for 6 categories
- 8 investments across 6 asset types
- 6 financial goals with varying progress
- 5 upcoming bills
- 6 sample notifications
- Sample JARVIS conversation

---

## Project Structure

```
smart-finance-insights/
├── app.py                      # Main Flask application & route registration
├── config.py                   # Configuration (DB path, secret key, etc.)
├── init_db.py                  # Database initialization & sample data seeding
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── finance.db                  # SQLite database (auto-created)
│
├── modules/                    # All business logic (Flask Blueprints)
│   ├── __init__.py
│   ├── auth.py                 # User auth: register, login, logout, profile
│   ├── expenses.py             # Income & expense transaction management
│   ├── budget.py               # Monthly budget planning & monitoring
│   ├── investments.py          # Investment portfolio + portfolio analytics
│   ├── goals.py                # Financial goal planning & tracking
│   ├── dashboard.py            # Main dashboard (combines all data)
│   ├── intelligence.py         # Analysis, recommendations, insights, health routes
│   ├── analysis.py             # Spending pattern analysis engine
│   ├── insights.py             # AI-based financial insights generator
│   ├── health_score.py         # Financial health score calculator
│   ├── notifications.py        # Alert & notification system
│   ├── reports.py              # Financial reports (4 types)
│   ├── export.py               # PDF & Excel export functionality
│   └── jarvis.py               # JARVIS AI Financial Assistant chatbot
│
├── utils/                      # Utility functions
│   ├── __init__.py
│   ├── db.py                   # Database connection helpers
│   └── helpers.py              # Currency formatting, auth decorator, etc.
│
├── templates/                  # Jinja2 HTML templates (18 pages)
│   ├── base.html               # Base layout with sidebar navigation
│   ├── login.html              # Login page
│   ├── register.html           # Registration page
│   ├── profile.html            # User profile management
│   ├── dashboard.html          # Main financial dashboard
│   ├── expenses.html           # Transaction management
│   ├── budget.html             # Budget planner
│   ├── investments.html        # Investment portfolio
│   ├── goals.html              # Financial goals
│   ├── analysis.html           # Spending pattern analysis
│   ├── budget_recommendations.html  # AI budget recommendations
│   ├── insights.html           # AI financial insights
│   ├── health_score.html       # Financial health score
│   ├── notifications.html      # Alerts & notifications
│   ├── reports.html            # Financial reports (4 types)
│   ├── portfolio_analytics.html # Portfolio analytics dashboard
│   ├── jarvis.html             # JARVIS chatbot interface
│   └── error.html              # Error pages (404/500)
│
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css           # Complete stylesheet (green theme)
│   └── js/
│       └── main.js             # JavaScript (charts, modals, JARVIS chat)
│
└── exports/                    # Generated PDF/Excel reports (auto-created)
```

---

## Module Documentation

### Authentication (`modules/auth.py`)
- `POST /register` — Create new user account
- `POST /login` — Authenticate user, create session
- `GET /logout` — Clear session
- `GET/POST /profile` — View/edit profile
- `POST /change-password` — Change password

### Expenses (`modules/expenses.py`)
- `GET /expenses` — List transactions (with filters)
- `POST /expenses/add` — Add income or expense
- `POST /expenses/edit/<id>` — Edit transaction
- `POST /expenses/delete/<type>/<id>` — Delete transaction
- `GET /api/transaction/<id>` — Get transaction (AJAX)

### Budget (`modules/budget.py`)
- `GET /budget` — View budgets with utilization
- `POST /budget/add` — Add/update budget
- `POST /budget/delete/<id>` — Delete budget

### Investments (`modules/investments.py`)
- `GET /investments` — Portfolio with P/L, ROI, allocation
- `POST /investments/add` — Add investment
- `POST /investments/edit/<id>` — Edit investment
- `POST /investments/delete/<id>` — Delete investment
- `GET /portfolio-analytics` — Analytics dashboard with growth charts & risk

### Goals (`modules/goals.py`)
- `GET /goals` — List goals with progress
- `POST /goals/add` — Create goal
- `POST /goals/edit/<id>` — Edit goal
- `POST /goals/contribute/<id>` — Add savings to goal
- `POST /goals/delete/<id>` — Delete goal

### Intelligence (`modules/intelligence.py` + analysis/insights/health_score)
- `GET /analysis` — Spending pattern analysis
- `GET /budget-recommendations` — AI budget recommendations
- `GET /insights` — AI financial insights
- `GET /health-score` — Financial health score

### Notifications (`modules/notifications.py`)
- `GET /notifications` — View all notifications (auto-generates new ones)
- `POST /notifications/<id>/mark-read` — Mark as read
- `POST /notifications/mark-all-read` — Mark all as read
- `POST /notifications/<id>/delete` — Delete notification
- `GET /api/notifications/count` — Count for badge (AJAX)

### Reports & Export (`modules/reports.py` + `modules/export.py`)
- `GET /reports?type=expense|budget|investment|goal` — View report
- `GET /export/pdf/<type>` — Download PDF
- `GET /export/excel/<type>` — Download Excel

### JARVIS AI Assistant (`modules/jarvis.py`)
- `GET /jarvis` — Chat interface
- `POST /jarvis/chat` — Send message, get AI response
- `POST /jarvis/clear` — Clear chat history

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/transaction/<id>` | GET | Get transaction details (for edit modal) |
| `/api/investment/<id>` | GET | Get investment details (for edit modal) |
| `/api/goal/<id>` | GET | Get goal details (for edit modal) |
| `/api/notifications/count` | GET | Get active notification count |
| `/jarvis/chat` | POST | Send message to JARVIS, get response |

---

## Screenshots

The dashboard includes:
- **Sidebar navigation** with 13 menu items grouped by category
- **Top bar** with search, notifications badge, JARVIS shortcut, user profile
- **Stat cards** with icons, values, and trend indicators
- **Interactive charts** (bar, doughnut, line) powered by Chart.js
- **Data tables** with badges, progress bars, and action buttons
- **Modal dialogs** for add/edit operations
- **Flash messages** for user feedback
- **Responsive design** that works on mobile and desktop
- **Sticky footer** at the bottom of every page

### Color Scheme
- Primary: Green (`#16a34a`)
- Income/Success: Emerald (`#10b981`)
- Expense/Danger: Red (`#ef4444`)
- Warning: Amber (`#f59e0b`)
- Background: Light gray (`#f8fafc`)
- Cards: White (`#ffffff`)

---

## Database Schema

| Table | Purpose |
|-------|---------|
| `users` | User accounts (name, email, password hash, phone, occupation, income) |
| `income` | Income records (source, amount, date, notes) |
| `expenses` | Expense records (category, description, amount, date) |
| `budgets` | Monthly budgets per category (amount, month, year) |
| `investments` | Investment holdings (asset_type, name, invested, current_value) |
| `goals` | Financial goals (name, target, saved, target_date, category) |
| `notifications` | Alert notifications (type, message, priority, status) |
| `bills` | Upcoming bills (name, amount, due_date, status) |
| `jarvis_chat` | JARVIS conversation history (role, message) |

---

## Development Notes

- **No external database server needed** — SQLite is file-based and included with Python
- **All passwords are hashed** using SHA-256 with a salt prefix
- **SQL injection prevention** — all queries use parameterized statements
- **Session security** — HTTPOnly cookies, configurable session lifetime
- **Input validation** — server-side validation on all forms
- **Responsive design** — mobile-first with breakpoints at 640px and 1024px

---

## License

This project is created for educational purposes as part of the Smart Finance Insights curriculum.

---

**Built with ❤️ using Python Flask**
