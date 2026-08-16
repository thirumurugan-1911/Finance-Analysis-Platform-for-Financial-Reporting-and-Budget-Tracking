"""
Budget Planning Module
Milestone 1 - Day 4
Features: Monthly budget creation, validation, remaining budget, progress tracking
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.db import query_db, execute_db
from utils.helpers import (login_required, get_current_month, get_current_year,
                           get_month_name, calculate_percentage)

bp = Blueprint('budget', __name__, url_prefix='')

BUDGET_CATEGORIES = ['Food', 'Shopping', 'Bills', 'Entertainment', 'Transport', 'Health', 'Education', 'Other']


@bp.route('/budget')
@login_required
def index():
    """Budget planning page."""
    user_id = session['user_id']
    month = int(request.args.get('month', get_current_month()))
    year = int(request.args.get('year', get_current_year()))

    # Get budgets for selected month
    budgets = query_db(
        """SELECT * FROM budgets WHERE user_id=? AND month=? AND year=? ORDER BY category""",
        (user_id, month, year)
    )

    # Get actual spending per category for the month
    budget_data = []
    total_budget = 0
    total_spent = 0
    for b in budgets:
        spent_row = query_db(
            """SELECT COALESCE(SUM(amount), 0) as total FROM expenses
               WHERE user_id=? AND category=? AND strftime('%m', date)=? AND strftime('%Y', date)=?""",
            (user_id, b['category'], f"{month:02d}", str(year)), one=True
        )
        spent = spent_row['total'] if spent_row else 0
        remaining = b['amount'] - spent
        pct = calculate_percentage(spent, b['amount'])
        status = 'exceeded' if remaining < 0 else ('warning' if pct >= 80 else 'good')
        budget_data.append({
            'id': b['id'], 'category': b['category'], 'budget': b['amount'],
            'spent': spent, 'remaining': remaining, 'percentage': pct, 'status': status
        })
        total_budget += b['amount']
        total_spent += spent

    total_remaining = total_budget - total_spent
    overall_pct = calculate_percentage(total_spent, total_budget)

    return render_template('budget.html',
                           budget_data=budget_data,
                           total_budget=total_budget,
                           total_spent=total_spent,
                           total_remaining=total_remaining,
                           overall_percentage=overall_pct,
                           categories=BUDGET_CATEGORIES,
                           selected_month=month,
                           selected_year=year,
                           month_name=get_month_name(month))


@bp.route('/budget/add', methods=['POST'])
@login_required
def add():
    """Add or update a budget."""
    user_id = session['user_id']
    category = request.form.get('category', '').strip()
    amount = float(request.form.get('amount', 0) or 0)
    month = int(request.form.get('month', get_current_month()))
    year = int(request.form.get('year', get_current_year()))

    if not category or amount <= 0:
        flash('Category and valid amount are required.', 'danger')
        return redirect(url_for('budget.index', month=month, year=year))

    # Check if budget exists for this category/month/year
    existing = query_db(
        "SELECT id FROM budgets WHERE user_id=? AND category=? AND month=? AND year=?",
        (user_id, category, month, year), one=True
    )
    if existing:
        execute_db("UPDATE budgets SET amount=? WHERE id=?", (amount, existing['id']))
        flash('Budget updated successfully!', 'success')
    else:
        execute_db(
            "INSERT INTO budgets (user_id, category, amount, month, year) VALUES (?, ?, ?, ?, ?)",
            (user_id, category, amount, month, year)
        )
        flash('Budget added successfully!', 'success')
    return redirect(url_for('budget.index', month=month, year=year))


@bp.route('/budget/delete/<int:budget_id>', methods=['POST'])
@login_required
def delete(budget_id):
    """Delete a budget."""
    user_id = session['user_id']
    execute_db("DELETE FROM budgets WHERE id=? AND user_id=?", (budget_id, user_id))
    flash('Budget deleted successfully!', 'success')
    return redirect(url_for('budget.index'))
