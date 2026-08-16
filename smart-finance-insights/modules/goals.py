"""
Financial Goal Planning Module
Milestone 2 - Module 3
Features: Create goals, set target amounts/dates, track progress, completion %
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from utils.db import query_db, execute_db
from utils.helpers import login_required, get_current_date, calculate_percentage
from datetime import datetime

bp = Blueprint('goals', __name__, url_prefix='')

GOAL_CATEGORIES = ['Savings', 'Travel', 'Property', 'Vehicle', 'Retirement', 'Education', 'Emergency', 'Other']
GOAL_SUGGESTIONS = ['Emergency Fund', 'Vacation Savings', 'Education Fund', 'Home Purchase',
                    'Vehicle Purchase', 'Retirement Planning', 'Wedding Fund', 'Debt Repayment']


@bp.route('/goals')
@login_required
def index():
    """Financial goals page."""
    user_id = session['user_id']
    goals = query_db("SELECT * FROM goals WHERE user_id=? ORDER BY target_date", (user_id,))

    goal_list = []
    total_target = 0
    total_saved = 0
    goals_achieved = 0
    for g in goals:
        saved = g['saved_amount']
        target = g['target_amount']
        pct = calculate_percentage(saved, target)
        remaining = target - saved
        achieved = saved >= target
        if achieved:
            goals_achieved += 1

        # Days remaining
        days_left = None
        status = 'On Track'
        if g['target_date']:
            try:
                target_date = datetime.strptime(g['target_date'], '%Y-%m-%d')
                days_left = (target_date - datetime.now()).days
                if days_left < 0:
                    status = 'Overdue'
                elif pct >= 100:
                    status = 'Achieved'
                elif pct >= 75:
                    status = 'On Track'
                elif pct >= 50:
                    status = 'Progress'
                else:
                    status = 'Behind'
            except ValueError:
                pass

        goal_list.append({
            'id': g['id'], 'name': g['goal_name'], 'target': target,
            'saved': saved, 'remaining': remaining, 'percentage': pct,
            'target_date': g['target_date'], 'category': g['category'],
            'achieved': achieved, 'days_left': days_left, 'status': status
        })
        total_target += target
        total_saved += saved

    completion_pct = calculate_percentage(total_saved, total_target)

    return render_template('goals.html',
                           goals=goal_list,
                           total_target=total_target,
                           total_saved=total_saved,
                           total_remaining=total_target - total_saved,
                           completion_pct=completion_pct,
                           goals_count=len(goal_list),
                           goals_achieved=goals_achieved,
                           categories=GOAL_CATEGORIES,
                           suggestions=GOAL_SUGGESTIONS)


@bp.route('/goals/add', methods=['POST'])
@login_required
def add():
    """Add a new financial goal."""
    user_id = session['user_id']
    name = request.form.get('name', '').strip()
    target = float(request.form.get('target', 0) or 0)
    saved = float(request.form.get('saved', 0) or 0)
    target_date = request.form.get('target_date', '')
    category = request.form.get('category', 'Savings')

    if not name or target <= 0:
        flash('Goal name and target amount are required.', 'danger')
        return redirect(url_for('goals.index'))

    execute_db(
        """INSERT INTO goals (user_id, goal_name, target_amount, saved_amount, target_date, category)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, name, target, saved, target_date, category)
    )
    flash('Goal added successfully!', 'success')
    return redirect(url_for('goals.index'))


@bp.route('/goals/edit/<int:goal_id>', methods=['POST'])
@login_required
def edit(goal_id):
    """Edit a goal."""
    user_id = session['user_id']
    name = request.form.get('name', '').strip()
    target = float(request.form.get('target', 0) or 0)
    saved = float(request.form.get('saved', 0) or 0)
    target_date = request.form.get('target_date', '')
    category = request.form.get('category', 'Savings')

    record = query_db("SELECT * FROM goals WHERE id=? AND user_id=?", (goal_id, user_id), one=True)
    if not record:
        flash('Goal not found.', 'danger')
        return redirect(url_for('goals.index'))

    execute_db(
        "UPDATE goals SET goal_name=?, target_amount=?, saved_amount=?, target_date=?, category=? WHERE id=? AND user_id=?",
        (name, target, saved, target_date, category, goal_id, user_id)
    )
    flash('Goal updated successfully!', 'success')
    return redirect(url_for('goals.index'))


@bp.route('/goals/contribute/<int:goal_id>', methods=['POST'])
@login_required
def contribute(goal_id):
    """Add savings to a goal."""
    user_id = session['user_id']
    amount = float(request.form.get('amount', 0) or 0)
    if amount <= 0:
        flash('Contribution amount must be greater than 0.', 'danger')
        return redirect(url_for('goals.index'))

    record = query_db("SELECT * FROM goals WHERE id=? AND user_id=?", (goal_id, user_id), one=True)
    if not record:
        flash('Goal not found.', 'danger')
        return redirect(url_for('goals.index'))

    new_saved = record['saved_amount'] + amount
    execute_db("UPDATE goals SET saved_amount=? WHERE id=? AND user_id=?", (new_saved, goal_id, user_id))
    flash(f'₹{amount:,.0f} contributed to {record["goal_name"]}!', 'success')
    return redirect(url_for('goals.index'))


@bp.route('/goals/delete/<int:goal_id>', methods=['POST'])
@login_required
def delete(goal_id):
    """Delete a goal."""
    user_id = session['user_id']
    execute_db("DELETE FROM goals WHERE id=? AND user_id=?", (goal_id, user_id))
    flash('Goal deleted successfully!', 'success')
    return redirect(url_for('goals.index'))


@bp.route('/api/goal/<int:goal_id>')
@login_required
def get_goal(goal_id):
    """API: Get goal for editing (AJAX)."""
    user_id = session['user_id']
    row = query_db("SELECT * FROM goals WHERE id=? AND user_id=?", (goal_id, user_id), one=True)
    if row:
        return jsonify({
            'id': row['id'], 'name': row['goal_name'], 'target': row['target_amount'],
            'saved': row['saved_amount'], 'target_date': row['target_date'], 'category': row['category']
        })
    return jsonify({'error': 'Not found'}), 404
