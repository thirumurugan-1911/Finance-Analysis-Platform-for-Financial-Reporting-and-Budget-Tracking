"""
Alert & Notification System Module
Milestone 3 - Day 4
Generates and manages notifications: budget alerts, bill reminders,
goal reminders, investment alerts, low balance warnings.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from utils.db import query_db, execute_db
from utils.helpers import login_required, calculate_percentage, get_current_month, get_current_year
from datetime import datetime, timedelta

bp = Blueprint('notifications', __name__, url_prefix='')


def get_active_notifications(user_id, limit=None):
    """Get active notifications for a user."""
    query = "SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC"
    if limit:
        query += f" LIMIT {limit}"
    return query_db(query, (user_id,))


def generate_notifications(user_id):
    """Auto-generate notifications based on current financial state."""
    month = get_current_month()
    year = get_current_year()
    month_str = f"{year}-{month:02d}"
    today = datetime.now()

    # Clear old auto-generated notifications
    execute_db("DELETE FROM notifications WHERE user_id=? AND message LIKE '%AUTO%'", (user_id,))

    # --- Budget alerts ---
    budgets = query_db(
        "SELECT * FROM budgets WHERE user_id=? AND month=? AND year=?",
        (user_id, month, year)
    )
    for b in (budgets or []):
        spent_row = query_db(
            """SELECT COALESCE(SUM(amount),0) as total FROM expenses
               WHERE user_id=? AND category=? AND strftime('%Y-%m', date)=?""",
            (user_id, b['category'], month_str), one=True
        )
        spent = spent_row['total'] if spent_row else 0
        pct = calculate_percentage(spent, b['amount'])
        if pct >= 100:
            over = spent - b['amount']
            execute_db(
                "INSERT INTO notifications (user_id, type, message, priority, status) VALUES (?, ?, ?, ?, ?)",
                (user_id, 'Budget Alert',
                 f'[AUTO] {b["category"]} expenses exceeded budget by ₹{over:,.0f}', 'High', 'Active')
            )
        elif pct >= 80:
            execute_db(
                "INSERT INTO notifications (user_id, type, message, priority, status) VALUES (?, ?, ?, ?, ?)",
                (user_id, 'Budget Alert',
                 f'[AUTO] {b["category"]} budget {pct:.0f}% used - approaching limit', 'Medium', 'Active')
            )

    # --- Bill reminders ---
    bills = query_db("SELECT * FROM bills WHERE user_id=? AND status='Pending'", (user_id,))
    for bill in (bills or []):
        try:
            due_date = datetime.strptime(bill['due_date'], '%Y-%m-%d')
            days_left = (due_date - today).days
            if 0 <= days_left <= 7:
                execute_db(
                    "INSERT INTO notifications (user_id, type, message, priority, status) VALUES (?, ?, ?, ?, ?)",
                    (user_id, 'Bill Reminder',
                     f'[AUTO] {bill["bill_name"]} due in {days_left} days (₹{bill["amount"]:,.0f})',
                     'High' if days_left <= 2 else 'Medium', 'Active')
                )
            elif days_left < 0:
                execute_db(
                    "INSERT INTO notifications (user_id, type, message, priority, status) VALUES (?, ?, ?, ?, ?)",
                    (user_id, 'Bill Overdue',
                     f'[AUTO] {bill["bill_name"]} is overdue by {abs(days_left)} days (₹{bill["amount"]:,.0f})',
                     'High', 'Active')
                )
        except ValueError:
            pass

    # --- Goal reminders ---
    goals = query_db("SELECT * FROM goals WHERE user_id=?", (user_id,))
    for g in (goals or []):
        pct = calculate_percentage(g['saved_amount'], g['target_amount'])
        if pct >= 100:
            execute_db(
                "INSERT INTO notifications (user_id, type, message, priority, status) VALUES (?, ?, ?, ?, ?)",
                (user_id, 'Goal Achieved',
                 f'[AUTO] Congratulations! {g["goal_name"]} goal achieved!', 'Medium', 'Completed')
            )
        elif g['target_date']:
            try:
                target_dt = datetime.strptime(g['target_date'], '%Y-%m-%d')
                days_left = (target_dt - today).days
                if 0 < days_left <= 30 and pct < 90:
                    execute_db(
                        "INSERT INTO notifications (user_id, type, message, priority, status) VALUES (?, ?, ?, ?, ?)",
                        (user_id, 'Goal Reminder',
                         f'[AUTO] {g["goal_name"]} goal due in {days_left} days - {pct:.0f}% complete',
                         'Medium', 'Active')
                    )
            except ValueError:
                pass

    # --- Investment alerts ---
    inv_row = query_db(
        "SELECT COALESCE(SUM(invested_amount),0) as invested, COALESCE(SUM(current_value),0) as current FROM investments WHERE user_id=?",
        (user_id,), one=True
    )
    if inv_row and inv_row['invested'] > 0:
        pl = inv_row['current'] - inv_row['invested']
        roi = calculate_percentage(pl, inv_row['invested'])
        if roi > 5:
            execute_db(
                "INSERT INTO notifications (user_id, type, message, priority, status) VALUES (?, ?, ?, ?, ?)",
                (user_id, 'Investment Alert',
                 f'[AUTO] Portfolio gained {roi:.1f}% (₹{pl:,.0f} profit)', 'Low', 'Completed')
            )
        elif roi < -5:
            execute_db(
                "INSERT INTO notifications (user_id, type, message, priority, status) VALUES (?, ?, ?, ?, ?)",
                (user_id, 'Investment Alert',
                 f'[AUTO] Portfolio down {abs(roi):.1f}% (₹{abs(pl):,.0f} loss) - review holdings', 'High', 'Active')
            )

    # --- Savings rate alert ---
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
    if total_income > 0:
        savings_rate = calculate_percentage(savings, total_income)
        if savings_rate < 10:
            execute_db(
                "INSERT INTO notifications (user_id, type, message, priority, status) VALUES (?, ?, ?, ?, ?)",
                (user_id, 'Low Savings',
                 f'[AUTO] Savings rate is only {savings_rate:.1f}% - increase savings urgently', 'High', 'Active')
            )


@bp.route('/notifications')
@login_required
def index():
    """Notifications page."""
    user_id = session['user_id']
    # Auto-generate fresh notifications
    generate_notifications(user_id)

    notifications = query_db(
        "SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC",
        (user_id,)
    )

    # Count by priority and status
    high_count = sum(1 for n in notifications if n['priority'] == 'High' and n['status'] == 'Active')
    medium_count = sum(1 for n in notifications if n['priority'] == 'Medium' and n['status'] == 'Active')
    active_count = sum(1 for n in notifications if n['status'] == 'Active')

    return render_template('notifications.html',
                           notifications=notifications,
                           high_count=high_count,
                           medium_count=medium_count,
                           active_count=active_count,
                           total_count=len(notifications))


@bp.route('/notifications/<int:notif_id>/mark-read', methods=['POST'])
@login_required
def mark_read(notif_id):
    """Mark a notification as read/completed."""
    user_id = session['user_id']
    execute_db("UPDATE notifications SET status='Completed' WHERE id=? AND user_id=?", (notif_id, user_id))
    flash('Notification marked as read.', 'success')
    return redirect(url_for('notifications.index'))


@bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_read():
    """Mark all notifications as read."""
    user_id = session['user_id']
    execute_db("UPDATE notifications SET status='Completed' WHERE user_id=?", (user_id,))
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('notifications.index'))


@bp.route('/notifications/<int:notif_id>/delete', methods=['POST'])
@login_required
def delete(notif_id):
    """Delete a notification."""
    user_id = session['user_id']
    execute_db("DELETE FROM notifications WHERE id=? AND user_id=?", (notif_id, user_id))
    flash('Notification deleted.', 'success')
    return redirect(url_for('notifications.index'))


@bp.route('/notifications/clear-all', methods=['POST'])
@login_required
def clear_all():
    """Clear all notifications."""
    user_id = session['user_id']
    execute_db("DELETE FROM notifications WHERE user_id=?", (user_id,))
    flash('All notifications cleared.', 'success')
    return redirect(url_for('notifications.index'))


@bp.route('/api/notifications/count')
@login_required
def count():
    """API: Get notification count for header badge."""
    user_id = session['user_id']
    row = query_db(
        "SELECT COUNT(*) as cnt FROM notifications WHERE user_id=? AND status='Active'",
        (user_id,), one=True
    )
    return jsonify({'count': row['cnt'] if row else 0})
