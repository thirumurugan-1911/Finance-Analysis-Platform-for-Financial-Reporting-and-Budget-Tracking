"""
Financial Reports Module
Milestone 4 - Day 1
Generates: Monthly Expense Report, Budget Utilization Report,
Investment Performance Report, Financial Goal Progress Report.
"""
from flask import Blueprint, render_template, request, session
from utils.db import query_db
from utils.helpers import (login_required, get_current_month, get_current_year,
                           get_month_name, calculate_percentage)
from datetime import datetime, timedelta

bp = Blueprint('reports', __name__, url_prefix='')


@bp.route('/reports')
@login_required
def index():
    """Reports overview page."""
    user_id = session['user_id']
    month = int(request.args.get('month', get_current_month()))
    year = int(request.args.get('year', get_current_year()))
    report_type = request.args.get('type', 'expense')
    month_str = f"{year}-{month:02d}"

    data = {}

    if report_type == 'expense':
        # --- Monthly Expense Report ---
        expenses = query_db(
            """SELECT category, description, amount, date FROM expenses
               WHERE user_id=? AND strftime('%Y-%m', date)=?
               ORDER BY date DESC, category""",
            (user_id, month_str)
        )
        cat_summary = query_db(
            """SELECT category, SUM(amount) as total, COUNT(*) as count FROM expenses
               WHERE user_id=? AND strftime('%Y-%m', date)=?
               GROUP BY category ORDER BY total DESC""",
            (user_id, month_str)
        )
        total = sum(c['total'] for c in cat_summary) if cat_summary else 0
        data = {
            'expenses': expenses,
            'cat_summary': cat_summary,
            'total': total,
            'count': len(expenses) if expenses else 0
        }

    elif report_type == 'budget':
        # --- Budget Utilization Report ---
        budgets = query_db(
            "SELECT * FROM budgets WHERE user_id=? AND month=? AND year=?",
            (user_id, month, year)
        )
        budget_report = []
        total_budget = 0
        total_spent = 0
        for b in (budgets or []):
            spent_row = query_db(
                """SELECT COALESCE(SUM(amount),0) as total FROM expenses
                   WHERE user_id=? AND category=? AND strftime('%Y-%m', date)=?""",
                (user_id, b['category'], month_str), one=True
            )
            spent = spent_row['total'] if spent_row else 0
            budget_report.append({
                'category': b['category'], 'budget': b['amount'],
                'spent': spent, 'remaining': b['amount'] - spent,
                'percentage': calculate_percentage(spent, b['amount']),
                'status': 'Exceeded' if spent > b['amount'] else ('Warning' if calculate_percentage(spent, b['amount']) >= 80 else 'Good')
            })
            total_budget += b['amount']
            total_spent += spent
        data = {
            'budget_report': budget_report,
            'total_budget': total_budget,
            'total_spent': total_spent,
            'total_remaining': total_budget - total_spent,
            'utilization': calculate_percentage(total_spent, total_budget)
        }

    elif report_type == 'investment':
        # --- Investment Performance Report ---
        investments = query_db("SELECT * FROM investments WHERE user_id=?", (user_id,))
        inv_report = []
        total_invested = 0
        total_current = 0
        for inv in (investments or []):
            pl = inv['current_value'] - inv['invested_amount']
            roi = calculate_percentage(pl, inv['invested_amount'])
            inv_report.append({
                'name': inv['investment_name'], 'asset': inv['asset_type'],
                'invested': inv['invested_amount'], 'current': inv['current_value'],
                'pl': pl, 'roi': roi,
                'status': 'Profit' if pl >= 0 else 'Loss'
            })
            total_invested += inv['invested_amount']
            total_current += inv['current_value']
        data = {
            'investments': inv_report,
            'total_invested': total_invested,
            'total_current': total_current,
            'total_pl': total_current - total_invested,
            'total_roi': calculate_percentage(total_current - total_invested, total_invested)
        }

    elif report_type == 'goal':
        # --- Goal Progress Report ---
        goals = query_db("SELECT * FROM goals WHERE user_id=? ORDER BY target_date", (user_id,))
        goal_report = []
        total_target = 0
        total_saved = 0
        achieved = 0
        for g in (goals or []):
            pct = calculate_percentage(g['saved_amount'], g['target_amount'])
            days_left = None
            if g['target_date']:
                try:
                    td = datetime.strptime(g['target_date'], '%Y-%m-%d')
                    days_left = (td - datetime.now()).days
                except ValueError:
                    pass
            goal_report.append({
                'name': g['goal_name'], 'category': g['category'],
                'target': g['target_amount'], 'saved': g['saved_amount'],
                'remaining': g['target_amount'] - g['saved_amount'],
                'percentage': pct, 'target_date': g['target_date'],
                'days_left': days_left, 'achieved': g['saved_amount'] >= g['target_amount']
            })
            total_target += g['target_amount']
            total_saved += g['saved_amount']
            if g['saved_amount'] >= g['target_amount']:
                achieved += 1
        data = {
            'goals': goal_report,
            'total_target': total_target,
            'total_saved': total_saved,
            'total_remaining': total_target - total_saved,
            'completion': calculate_percentage(total_saved, total_target),
            'achieved': achieved,
            'total_goals': len(goals) if goals else 0
        }

    return render_template('reports.html',
                           report_type=report_type,
                           data=data,
                           selected_month=month,
                           selected_year=year,
                           month_name=get_month_name(month))
