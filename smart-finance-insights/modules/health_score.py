"""
Financial Health Score Module
Milestone 3 - Day 3
Calculates overall financial health using income, expenses, savings, investments, debt.
Score criteria: Savings Ratio, Investment Growth, Debt-to-Income, Expense Ratio.
Status: Excellent / Good / Fair / Poor.
"""
from utils.db import query_db
from utils.helpers import calculate_percentage, get_current_month, get_current_year


def get_health_score(user_id):
    """Calculate comprehensive financial health score (0-100)."""
    month = get_current_month()
    year = get_current_year()
    month_str = f"{year}-{month:02d}"

    # --- Gather financial data ---
    income_row = query_db(
        "SELECT COALESCE(SUM(amount),0) as total FROM income WHERE user_id=? AND strftime('%Y-%m', date)=?",
        (user_id, month_str), one=True
    )
    expense_row = query_db(
        "SELECT COALESCE(SUM(amount),0) as total FROM expenses WHERE user_id=? AND strftime('%Y-%m', date)=?",
        (user_id, month_str), one=True
    )
    inv_row = query_db(
        "SELECT COALESCE(SUM(invested_amount),0) as invested, COALESCE(SUM(current_value),0) as current FROM investments WHERE user_id=?",
        (user_id,), one=True
    )

    total_income = income_row['total'] if income_row else 0
    total_expense = expense_row['total'] if expense_row else 0
    savings = total_income - total_expense
    total_invested = inv_row['invested'] if inv_row else 0
    total_current = inv_row['current'] if inv_row else 0

    # Simulated debt (could be a real table; using 15% of income as example debt)
    outstanding_loan = total_income * 1.5  # Approximate debt
    emergency_fund = 0
    emergency_goal = query_db(
        "SELECT saved_amount FROM goals WHERE user_id=? AND (goal_name LIKE '%emergency%' OR category='Emergency')",
        (user_id,), one=True
    )
    if emergency_goal:
        emergency_fund = emergency_goal['saved_amount']

    # --- Calculate indicators ---
    savings_ratio = calculate_percentage(savings, total_income)
    expense_ratio = calculate_percentage(total_expense, total_income)
    investment_growth = calculate_percentage(total_current - total_invested, total_invested) if total_invested > 0 else 0
    debt_to_income = calculate_percentage(outstanding_loan, total_income * 12)  # Annual
    investment_ratio = calculate_percentage(total_current, total_income * 12) if total_income > 0 else 0

    # Emergency fund coverage (months)
    emergency_months = emergency_fund / total_expense if total_expense > 0 else 0

    # --- Scoring (0-100) ---
    # Savings Ratio score (30 points max) - 30%+ = full marks
    savings_score = min(savings_ratio / 30 * 30, 30)

    # Investment ratio score (25 points) - 50%+ of annual income = full
    investment_score = min(investment_ratio / 50 * 25, 25)

    # Debt-to-income score (20 points) - <20% = full, >50% = 0
    if debt_to_income <= 20:
        debt_score = 20
    elif debt_to_income >= 50:
        debt_score = 0
    else:
        debt_score = 20 - ((debt_to_income - 20) / 30) * 20

    # Expense ratio score (15 points) - <60% = full, >90% = 0
    if expense_ratio <= 60:
        expense_score = 15
    elif expense_ratio >= 90:
        expense_score = 0
    else:
        expense_score = 15 - ((expense_ratio - 60) / 30) * 15

    # Emergency fund score (10 points) - 6+ months = full
    emergency_score = min(emergency_months / 6 * 10, 10)

    total_score = round(savings_score + investment_score + debt_score + expense_score + emergency_score)

    # --- Status ---
    if total_score >= 80:
        status = 'Excellent'
        status_color = 'success'
    elif total_score >= 60:
        status = 'Good'
        status_color = 'info'
    elif total_score >= 40:
        status = 'Fair'
        status_color = 'warning'
    else:
        status = 'Poor'
        status_color = 'danger'

    # --- Recommendations ---
    recommendations = []
    if savings_ratio < 20:
        recommendations.append('Increase monthly savings to at least 20% of income.')
    if savings_ratio >= 30:
        recommendations.append('Maintain savings above 30% of income - excellent!')
    if investment_ratio < 50:
        recommendations.append(f'Increase monthly SIP to grow investments (currently {investment_ratio:.0f}% of annual income).')
    if debt_to_income > 30:
        recommendations.append('Focus on reducing outstanding debt to improve debt-to-income ratio.')
    if debt_to_income <= 20:
        recommendations.append('Continue maintaining a low debt ratio.')
    if expense_ratio > 70:
        recommendations.append('Reduce discretionary spending to lower expense ratio.')
    if emergency_months < 6:
        recommendations.append(f'Build emergency fund to cover 6 months of expenses (currently {emergency_months:.1f} months).')
    if emergency_months >= 6:
        recommendations.append('Emergency fund is sufficient - great safety net!')

    return {
        'score': total_score,
        'status': status,
        'status_color': status_color,
        'indicators': {
            'savings_ratio': savings_ratio,
            'expense_ratio': expense_ratio,
            'investment_growth': investment_growth,
            'debt_to_income': debt_to_income,
            'investment_ratio': investment_ratio,
            'emergency_months': emergency_months
        },
        'score_breakdown': {
            'savings': round(savings_score),
            'investment': round(investment_score),
            'debt': round(debt_score),
            'expense': round(expense_score),
            'emergency': round(emergency_score)
        },
        'financial_data': {
            'monthly_income': total_income,
            'monthly_expenses': total_expense,
            'monthly_savings': savings,
            'total_investments': total_current,
            'outstanding_loan': outstanding_loan,
            'emergency_fund': emergency_fund
        },
        'recommendations': recommendations
    }
