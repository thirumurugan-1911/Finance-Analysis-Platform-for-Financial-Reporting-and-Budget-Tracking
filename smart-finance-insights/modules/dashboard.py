"""
Main Financial Dashboard Module
Milestone 1 - Day 5 & Milestone 3 - Day 6 (Intelligence Dashboard)
Combines: summary cards, charts, transaction history, spending analysis,
budget recommendations, AI insights, notifications, goal progress.
"""
from flask import Blueprint, render_template, session, redirect, url_for
from utils.db import query_db
from utils.helpers import (login_required, get_current_month, get_current_year,
                           get_month_name, calculate_percentage)
from modules.analysis import get_spending_analysis
from modules.insights import get_ai_insights
from modules.health_score import get_health_score
from modules.notifications import get_active_notifications

bp = Blueprint('dashboard', __name__, url_prefix='')


@bp.route('/dashboard')
@login_required
def index():
    """Main dashboard - combines all financial data."""
    user_id = session['user_id']
    month = get_current_month()
    year = get_current_year()
    month_str = f"{year}-{month:02d}"

    # --- Summary Totals (current month) ---
    income_row = query_db(
        "SELECT COALESCE(SUM(amount),0) as total FROM income WHERE user_id=? AND strftime('%Y-%m', date)=?",
        (user_id, month_str), one=True
    )
    expense_row = query_db(
        "SELECT COALESCE(SUM(amount),0) as total FROM expenses WHERE user_id=? AND strftime('%Y-%m', date)=?",
        (user_id, month_str), one=True
    )
    total_income = income_row['total'] if income_row else 0
    total_expense = expense_row['total'] if expense_row else 0
    savings = total_income - total_expense
    savings_rate = calculate_percentage(savings, total_income)

    # --- Investment totals ---
    inv_row = query_db(
        "SELECT COALESCE(SUM(invested_amount),0) as invested, COALESCE(SUM(current_value),0) as current FROM investments WHERE user_id=?",
        (user_id,), one=True
    )
    total_invested = inv_row['invested'] if inv_row else 0
    total_current = inv_row['current'] if inv_row else 0
    investment_pl = total_current - total_invested

    # --- Budget status ---
    budget_row = query_db(
        "SELECT COALESCE(SUM(amount),0) as total FROM budgets WHERE user_id=? AND month=? AND year=?",
        (user_id, month, year), one=True
    )
    total_budget = budget_row['total'] if budget_row else 0
    budget_used_pct = calculate_percentage(total_expense, total_budget)

    # --- Category-wise expenses (for pie chart) ---
    cat_rows = query_db(
        """SELECT category, SUM(amount) as total FROM expenses
           WHERE user_id=? AND strftime('%Y-%m', date)=?
           GROUP BY category ORDER BY total DESC""",
        (user_id, month_str)
    )
    category_expenses = [{'category': r['category'], 'amount': r['total']} for r in cat_rows]

    # --- Income vs Expense (6 months) for line chart ---
    income_expense_data = []
    from datetime import datetime, timedelta
    today = datetime.now()
    for i in range(5, -1, -1):
        d = today - timedelta(days=i * 30)
        m_str = d.strftime('%Y-%m')
        inc = query_db("SELECT COALESCE(SUM(amount),0) as t FROM income WHERE user_id=? AND strftime('%Y-%m', date)=?",
                       (user_id, m_str), one=True)
        exp = query_db("SELECT COALESCE(SUM(amount),0) as t FROM expenses WHERE user_id=? AND strftime('%Y-%m', date)=?",
                       (user_id, m_str), one=True)
        income_expense_data.append({
            'month': d.strftime('%b'),
            'income': inc['t'] if inc else 0,
            'expense': exp['t'] if exp else 0
        })

    # --- Recent transactions ---
    recent_expenses = query_db(
        """SELECT * FROM expenses WHERE user_id=? ORDER BY date DESC, id DESC LIMIT 5""",
        (user_id,)
    )
    recent_income = query_db(
        """SELECT * FROM income WHERE user_id=? ORDER BY date DESC, id DESC LIMIT 3""",
        (user_id,)
    )
    recent_transactions = []
    for e in recent_expenses:
        recent_transactions.append({'date': e['date'], 'desc': e['description'] or e['category'],
                                    'category': e['category'], 'amount': e['amount'], 'type': 'Expense'})
    for i in recent_income:
        recent_transactions.append({'date': i['date'], 'desc': i['notes'] or i['source'],
                                    'category': i['source'], 'amount': i['amount'], 'type': 'Income'})
    recent_transactions.sort(key=lambda x: x['date'], reverse=True)
    recent_transactions = recent_transactions[:8]

    # --- Goal progress ---
    goals = query_db("SELECT * FROM goals WHERE user_id=? ORDER BY target_date LIMIT 4", (user_id,))
    goal_progress = []
    for g in goals:
        pct = calculate_percentage(g['saved_amount'], g['target_amount'])
        goal_progress.append({
            'name': g['goal_name'], 'saved': g['saved_amount'],
            'target': g['target_amount'], 'percentage': min(pct, 100)
        })

    # --- Intelligence features ---
    spending_analysis = get_spending_analysis(user_id, month, year)
    ai_insights = get_ai_insights(user_id)
    health_score = get_health_score(user_id)
    notifications = get_active_notifications(user_id, limit=5)

    return render_template('dashboard.html',
                           total_income=total_income,
                           total_expense=total_expense,
                           savings=savings,
                           savings_rate=savings_rate,
                           total_invested=total_invested,
                           total_current=total_current,
                           investment_pl=investment_pl,
                           total_budget=total_budget,
                           budget_used_pct=budget_used_pct,
                           category_expenses=category_expenses,
                           income_expense_data=income_expense_data,
                           recent_transactions=recent_transactions,
                           goal_progress=goal_progress,
                           spending_analysis=spending_analysis,
                           ai_insights=ai_insights,
                           health_score=health_score,
                           notifications=notifications,
                           month_name=get_month_name(month),
                           year=year)
