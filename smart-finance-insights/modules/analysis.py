"""
Spending Pattern Analysis Module
Milestone 3 - Day 1
Analyzes user expenses: category-wise, monthly trends, identifies spending habits.
"""
from utils.db import query_db
from utils.helpers import calculate_percentage, get_month_name


def get_spending_analysis(user_id, month=None, year=None):
    """Get comprehensive spending analysis for a user."""
    from utils.helpers import get_current_month, get_current_year
    if month is None:
        month = get_current_month()
    if year is None:
        year = get_current_year()
    month_str = f"{year}-{month:02d}"

    # Category-wise spending for the month
    cat_rows = query_db(
        """SELECT category, SUM(amount) as total, COUNT(*) as count FROM expenses
           WHERE user_id=? AND strftime('%Y-%m', date)=?
           GROUP BY category ORDER BY total DESC""",
        (user_id, month_str)
    )

    total_expense = sum(r['total'] for r in cat_rows) if cat_rows else 0

    categories = []
    for r in cat_rows:
        categories.append({
            'category': r['category'],
            'amount': r['total'],
            'count': r['count'],
            'percentage': calculate_percentage(r['total'], total_expense),
            'avg_per_txn': r['total'] / r['count'] if r['count'] > 0 else 0
        })

    # Monthly trend (last 6 months)
    from datetime import datetime, timedelta
    today = datetime.now()
    monthly_trend = []
    for i in range(5, -1, -1):
        d = today - timedelta(days=i * 30)
        m_str = d.strftime('%Y-%m')
        row = query_db(
            "SELECT COALESCE(SUM(amount),0) as total FROM expenses WHERE user_id=? AND strftime('%Y-%m', date)=?",
            (user_id, m_str), one=True
        )
        monthly_trend.append({
            'month': d.strftime('%b'),
            'amount': row['total'] if row else 0
        })

    # Identify high spending categories (>15% of total)
    high_spending = [c for c in categories if c['percentage'] >= 15]

    # Average daily spending
    from datetime import datetime as dt
    days_in_month = 30
    avg_daily = total_expense / days_in_month if total_expense > 0 else 0

    return {
        'categories': categories,
        'total_expense': total_expense,
        'monthly_trend': monthly_trend,
        'high_spending': high_spending,
        'avg_daily': avg_daily,
        'month_name': get_month_name(month),
        'year': year,
        'transaction_count': sum(c['count'] for c in categories)
    }


def get_budget_recommendations(user_id, month=None, year=None):
    """Generate personalized budget recommendations based on spending history."""
    from utils.helpers import get_current_month, get_current_year
    if month is None:
        month = get_current_month()
    if year is None:
        year = get_current_year()
    month_str = f"{year}-{month:02d}"

    # Current month spending by category
    spending = query_db(
        """SELECT category, SUM(amount) as total FROM expenses
           WHERE user_id=? AND strftime('%Y-%m', date)=?
           GROUP BY category""",
        (user_id, month_str)
    )

    # Current budgets
    budgets = query_db(
        "SELECT category, amount FROM budgets WHERE user_id=? AND month=? AND year=?",
        (user_id, month, year)
    )
    budget_map = {b['category']: b['amount'] for b in budgets} if budgets else {}

    # Last 3 months average spending per category
    from datetime import datetime, timedelta
    today = datetime.now()
    three_months_ago = (today - timedelta(days=90)).strftime('%Y-%m')
    avg_spending = query_db(
        """SELECT category, AVG(monthly_total) as avg_total FROM (
              SELECT category, strftime('%Y-%m', date) as ym, SUM(amount) as monthly_total
              FROM expenses WHERE user_id=? AND date >= ?
              GROUP BY category, ym
           ) GROUP BY category""",
        (user_id, three_months_ago + '-01')
    )
    avg_map = {r['category']: r['avg_total'] for r in avg_spending} if avg_spending else {}

    recommendations = []
    for s in (spending or []):
        cat = s['category']
        spent = s['total']
        budget = budget_map.get(cat, 0)
        avg = avg_map.get(cat, spent)

        if budget > 0:
            pct = calculate_percentage(spent, budget)
            if pct > 100:
                over = spent - budget
                recommendations.append({
                    'category': cat, 'type': 'reduce', 'amount': over,
                    'message': f'Reduce {cat} spending by ₹{over:,.0f} - exceeded budget by {pct-100:.0f}%',
                    'priority': 'High'
                })
            elif pct >= 80:
                recommendations.append({
                    'category': cat, 'type': 'warning', 'amount': budget - spent,
                    'message': f'Watch {cat} spending - {pct:.0f}% of budget used',
                    'priority': 'Medium'
                })
            else:
                recommendations.append({
                    'category': cat, 'type': 'good', 'amount': budget - spent,
                    'message': f'{cat} spending is under control ({pct:.0f}% used)',
                    'priority': 'Low'
                })
        else:
            # No budget set - recommend one based on average
            recommended_budget = round(avg * 1.1 / 100) * 100  # 10% above avg, rounded
            recommendations.append({
                'category': cat, 'type': 'set_budget', 'amount': recommended_budget,
                'message': f'Set a budget of ₹{recommended_budget:,.0f} for {cat} (based on avg spending)',
                'priority': 'Medium'
            })

    # Savings recommendation
    income_row = query_db(
        "SELECT COALESCE(SUM(amount),0) as total FROM income WHERE user_id=? AND strftime('%Y-%m', date)=?",
        (user_id, month_str), one=True
    )
    total_income = income_row['total'] if income_row else 0
    total_expense = sum(s['total'] for s in spending) if spending else 0
    savings = total_income - total_expense
    savings_rate = calculate_percentage(savings, total_income)

    if savings_rate < 20:
        recommendations.append({
            'category': 'Savings', 'type': 'increase_savings',
            'amount': total_income * 0.2 - savings if savings < total_income * 0.2 else 0,
            'message': f'Increase monthly savings to at least 20% of income (currently {savings_rate:.0f}%)',
            'priority': 'High'
        })

    return {
        'recommendations': recommendations,
        'total_income': total_income,
        'total_expense': total_expense,
        'savings': savings,
        'savings_rate': savings_rate
    }
