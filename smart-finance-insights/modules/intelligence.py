"""
Intelligence & Insights Routes Module
Milestone 3 - Routes for spending analysis, budget recommendations, AI insights.
"""
from flask import Blueprint, render_template, request, session
from utils.db import query_db
from utils.helpers import (login_required, get_current_month, get_current_year,
                           get_month_name, calculate_percentage)
from modules.analysis import get_spending_analysis, get_budget_recommendations
from modules.insights import get_ai_insights

bp = Blueprint('intelligence', __name__, url_prefix='')


@bp.route('/analysis')
@login_required
def analysis():
    """Spending Pattern Analysis page."""
    user_id = session['user_id']
    month = int(request.args.get('month', get_current_month()))
    year = int(request.args.get('year', get_current_year()))
    data = get_spending_analysis(user_id, month, year)
    return render_template('analysis.html', data=data,
                           selected_month=month, selected_year=year)


@bp.route('/budget-recommendations')
@login_required
def budget_recommendations():
    """Personalized Budget Recommendations page."""
    user_id = session['user_id']
    month = int(request.args.get('month', get_current_month()))
    year = int(request.args.get('year', get_current_year()))
    data = get_budget_recommendations(user_id, month, year)
    return render_template('budget_recommendations.html', data=data,
                           selected_month=month, selected_year=year,
                           month_name=get_month_name(month))


@bp.route('/insights')
@login_required
def insights():
    """AI Financial Insights page."""
    user_id = session['user_id']
    data = get_ai_insights(user_id)
    return render_template('insights.html', data=data)


@bp.route('/health-score')
@login_required
def health_score():
    """Financial Health Score page."""
    user_id = session['user_id']
    from modules.health_score import get_health_score
    data = get_health_score(user_id)
    return render_template('health_score.html', data=data)
