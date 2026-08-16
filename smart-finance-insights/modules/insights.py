"""
AI-Based Financial Insights Module
Milestone 3 - Day 5
Generates personalized financial suggestions based on spending behavior.
"""
from utils.db import query_db
from utils.helpers import calculate_percentage, get_current_month, get_current_year
from datetime import datetime, timedelta


def get_ai_insights(user_id):
    """Generate AI-based financial insights for the user."""
    month = get_current_month()
    year = get_current_year()
    month_str = f"{year}-{month:02d}"

    # Current month financial data
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
    expense_rate = calculate_percentage(total_expense, total_income)

    insights = []

    # --- Savings insights ---
    if savings_rate >= 30:
        insights.append({
            'icon': 'check-circle', 'type': 'success', 'category': 'Savings',
            'title': 'Healthy Savings Rate',
            'message': f'Your savings rate is {savings_rate:.1f}% - excellent! You\'re saving ₹{savings:,.0f} this month.'
        })
    elif savings_rate >= 20:
        insights.append({
            'icon': 'trending-up', 'type': 'info', 'category': 'Savings',
            'title': 'Good Savings Progress',
            'message': f'Your savings rate is {savings_rate:.1f}%. Aim for 30%+ for optimal financial health.'
        })
    else:
        insights.append({
            'icon': 'alert-triangle', 'type': 'warning', 'category': 'Savings',
            'title': 'Low Savings Rate',
            'message': f'Your savings rate is only {savings_rate:.1f}%. Consider reducing expenses to save more.'
        })

    # --- Expense ratio insight ---
    if expense_rate > 80:
        insights.append({
            'icon': 'alert-circle', 'type': 'danger', 'category': 'Expenses',
            'title': 'High Expense Ratio',
            'message': f'You\'re spending {expense_rate:.1f}% of your income. Reduce discretionary spending urgently.'
        })

    # --- Category-wise insights ---
    cat_rows = query_db(
        """SELECT category, SUM(amount) as total FROM expenses
           WHERE user_id=? AND strftime('%Y-%m', date)=?
           GROUP BY category ORDER BY total DESC LIMIT 3""",
        (user_id, month_str)
    )
    if cat_rows:
        top_cat = cat_rows[0]
        insights.append({
            'icon': 'bar-chart', 'type': 'info', 'category': 'Spending',
            'title': f'Top Spending Category: {top_cat["category"]}',
            'message': f'You spent ₹{top_cat["total"]:,.0f} on {top_cat["category"]} this month ({calculate_percentage(top_cat["total"], total_expense):.1f}% of expenses).'
        })

    # --- Investment insights ---
    inv_row = query_db(
        "SELECT COALESCE(SUM(invested_amount),0) as invested, COALESCE(SUM(current_value),0) as current FROM investments WHERE user_id=?",
        (user_id,), one=True
    )
    if inv_row and inv_row['invested'] > 0:
        pl = inv_row['current'] - inv_row['invested']
        roi = calculate_percentage(pl, inv_row['invested'])
        if roi > 0:
            insights.append({
                'icon': 'trending-up', 'type': 'success', 'category': 'Investment',
                'title': 'Portfolio Gaining',
                'message': f'Your investment portfolio gained {roi:.1f}% (₹{pl:,.0f} profit). Keep up the good work!'
            })
        else:
            insights.append({
                'icon': 'trending-down', 'type': 'warning', 'category': 'Investment',
                'title': 'Portfolio Underperforming',
                'message': f'Your portfolio is down {abs(roi):.1f}% (₹{abs(pl):,.0f} loss). Consider rebalancing.'
            })

        # Investment to income ratio
        inv_ratio = calculate_percentage(inv_row['current'], total_income * 12) if total_income > 0 else 0
        if inv_ratio < 50:
            insights.append({
                'icon': 'piggy-bank', 'type': 'info', 'category': 'Investment',
                'title': 'Increase Investments',
                'message': f'Your investments are {inv_ratio:.1f}% of annual income. Aim for 100%+ through monthly SIPs.'
            })

    # --- Goal insights ---
    goals = query_db("SELECT * FROM goals WHERE user_id=?", (user_id,))
    if goals:
        achieved = sum(1 for g in goals if g['saved_amount'] >= g['target_amount'])
        insights.append({
            'icon': 'target', 'type': 'success', 'category': 'Goals',
            'title': 'Goal Progress',
            'message': f'You\'ve achieved {achieved} of {len(goals)} financial goals. Keep tracking your progress!'
        })

    # --- Emergency fund insight ---
    emergency_goal = query_db(
        "SELECT * FROM goals WHERE user_id=? AND (goal_name LIKE '%emergency%' OR category='Emergency')",
        (user_id,), one=True
    )
    if emergency_goal:
        months_covered = emergency_goal['saved_amount'] / total_expense if total_expense > 0 else 0
        if months_covered >= 6:
            insights.append({
                'icon': 'shield', 'type': 'success', 'category': 'Safety',
                'title': 'Strong Emergency Fund',
                'message': f'Your emergency fund covers {months_covered:.1f} months of expenses. Excellent safety net!'
            })
        elif months_covered >= 3:
            insights.append({
                'icon': 'shield', 'type': 'info', 'category': 'Safety',
                'title': 'Building Emergency Fund',
                'message': f'Emergency fund covers {months_covered:.1f} months. Aim for 6 months coverage.'
            })
        else:
            insights.append({
                'icon': 'shield', 'type': 'warning', 'category': 'Safety',
                'title': 'Low Emergency Fund',
                'message': f'Emergency fund only covers {months_covered:.1f} months. Build it up to 6 months.'
            })

    # --- Monthly comparison ---
    last_month = (datetime.now() - timedelta(days=30)).strftime('%Y-%m')
    last_exp_row = query_db(
        "SELECT COALESCE(SUM(amount),0) as total FROM expenses WHERE user_id=? AND strftime('%Y-%m', date)=?",
        (user_id, last_month), one=True
    )
    last_expense = last_exp_row['total'] if last_exp_row else 0
    if last_expense > 0:
        change = ((total_expense - last_expense) / last_expense) * 100
        if change > 10:
            insights.append({
                'icon': 'trending-up', 'type': 'warning', 'category': 'Trend',
                'title': 'Spending Increased',
                'message': f'Your spending increased {change:.1f}% compared to last month. Review your expenses.'
            })
        elif change < -10:
            insights.append({
                'icon': 'trending-down', 'type': 'success', 'category': 'Trend',
                'title': 'Spending Decreased',
                'message': f'Great job! Your spending decreased {abs(change):.1f}% compared to last month.'
            })

    return {
        'insights': insights,
        'total_income': total_income,
        'total_expense': total_expense,
        'savings': savings,
        'savings_rate': savings_rate,
        'expense_rate': expense_rate
    }
