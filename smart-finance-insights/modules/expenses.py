"""
Expense & Income Management Module
Milestone 1 - Day 3
Features: Add/Edit/Delete income & expenses, categorization, transaction history
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from utils.db import query_db, execute_db
from utils.helpers import login_required, get_current_date, get_current_month, get_current_year, get_month_name

bp = Blueprint('expenses', __name__, url_prefix='')

EXPENSE_CATEGORIES = ['Food', 'Shopping', 'Bills', 'Entertainment', 'Transport', 'Health', 'Education', 'Other']
INCOME_SOURCES = ['Salary', 'Freelance', 'Business', 'Investment', 'Rental', 'Gift', 'Other']


@bp.route('/expenses')
@login_required
def index():
    """Expense & income management page."""
    user_id = session['user_id']

    # Filters
    filter_type = request.args.get('type', 'all')
    filter_category = request.args.get('category', 'all')
    filter_month = request.args.get('month', str(get_current_month()))
    filter_year = request.args.get('year', str(get_current_year()))

    month = int(filter_month) if filter_month else get_current_month()
    year = int(filter_year) if filter_year else get_current_year()

    # Build expense query
    exp_query = "SELECT * FROM expenses WHERE user_id=? AND strftime('%m', date)=? AND strftime('%Y', date)=?"
    exp_args = [user_id, f"{month:02d}", str(year)]
    if filter_category != 'all':
        exp_query += " AND category=?"
        exp_args.append(filter_category)
    exp_query += " ORDER BY date DESC, id DESC"
    expenses = query_db(exp_query, tuple(exp_args))

    # Income query
    inc_query = "SELECT * FROM income WHERE user_id=? AND strftime('%m', date)=? AND strftime('%Y', date)=? ORDER BY date DESC, id DESC"
    incomes = query_db(inc_query, (user_id, f"{month:02d}", str(year)))

    # Combine into transaction list
    transactions = []
    if filter_type in ('all', 'expense'):
        for e in expenses:
            transactions.append({
                'id': e['id'], 'type': 'Expense', 'category': e['category'],
                'description': e['description'] or e['category'],
                'amount': e['amount'], 'date': e['date']
            })
    if filter_type in ('all', 'income'):
        for i in incomes:
            transactions.append({
                'id': i['id'], 'type': 'Income', 'category': i['source'],
                'description': i['notes'] or i['source'],
                'amount': i['amount'], 'date': i['date']
            })
    transactions.sort(key=lambda x: x['date'], reverse=True)

    # Totals for the month
    total_expense = sum(e['amount'] for e in expenses)
    total_income = sum(i['amount'] for i in incomes)

    return render_template('expenses.html',
                           transactions=transactions,
                           total_expense=total_expense,
                           total_income=total_income,
                           balance=total_income - total_expense,
                           categories=EXPENSE_CATEGORIES,
                           sources=INCOME_SOURCES,
                           filter_type=filter_type,
                           filter_category=filter_category,
                           selected_month=month,
                           selected_year=year,
                           month_name=get_month_name(month))


@bp.route('/expenses/add', methods=['POST'])
@login_required
def add():
    """Add a new expense or income."""
    user_id = session['user_id']
    txn_type = request.form.get('type', 'expense')
    category = request.form.get('category', '').strip()
    description = request.form.get('description', '').strip()
    amount = float(request.form.get('amount', 0) or 0)
    date = request.form.get('date', get_current_date())

    if amount <= 0:
        flash('Amount must be greater than 0.', 'danger')
        return redirect(url_for('expenses.index'))
    if not category:
        flash('Category is required.', 'danger')
        return redirect(url_for('expenses.index'))

    if txn_type == 'income':
        execute_db(
            "INSERT INTO income (user_id, source, amount, date, notes) VALUES (?, ?, ?, ?, ?)",
            (user_id, category, amount, date, description)
        )
        flash('Income added successfully!', 'success')
    else:
        execute_db(
            "INSERT INTO expenses (user_id, category, description, amount, date) VALUES (?, ?, ?, ?, ?)",
            (user_id, category, description, amount, date)
        )
        flash('Expense added successfully!', 'success')
    return redirect(url_for('expenses.index'))


@bp.route('/expenses/edit/<int:txn_id>', methods=['POST'])
@login_required
def edit(txn_id):
    """Edit an existing transaction."""
    user_id = session['user_id']
    txn_type = request.form.get('type', 'expense')
    category = request.form.get('category', '').strip()
    description = request.form.get('description', '').strip()
    amount = float(request.form.get('amount', 0) or 0)
    date = request.form.get('date', get_current_date())

    if txn_type == 'income':
        record = query_db("SELECT * FROM income WHERE id=? AND user_id=?", (txn_id, user_id), one=True)
        if not record:
            flash('Transaction not found.', 'danger')
            return redirect(url_for('expenses.index'))
        execute_db(
            "UPDATE income SET source=?, amount=?, date=?, notes=? WHERE id=? AND user_id=?",
            (category, amount, date, description, txn_id, user_id)
        )
    else:
        record = query_db("SELECT * FROM expenses WHERE id=? AND user_id=?", (txn_id, user_id), one=True)
        if not record:
            flash('Transaction not found.', 'danger')
            return redirect(url_for('expenses.index'))
        execute_db(
            "UPDATE expenses SET category=?, description=?, amount=?, date=? WHERE id=? AND user_id=?",
            (category, description, amount, date, txn_id, user_id)
        )
    flash('Transaction updated successfully!', 'success')
    return redirect(url_for('expenses.index'))


@bp.route('/expenses/delete/<txn_type>/<int:txn_id>', methods=['POST'])
@login_required
def delete(txn_type, txn_id):
    """Delete a transaction."""
    user_id = session['user_id']
    table = 'income' if txn_type == 'income' else 'expenses'
    execute_db(f"DELETE FROM {table} WHERE id=? AND user_id=?", (txn_id, user_id))
    flash('Transaction deleted successfully!', 'success')
    return redirect(url_for('expenses.index'))


@bp.route('/api/transaction/<int:txn_id>')
@login_required
def get_transaction(txn_id):
    """API: Get transaction details for editing (AJAX)."""
    user_id = session['user_id']
    txn_type = request.args.get('type', 'expense')
    if txn_type == 'income':
        row = query_db("SELECT * FROM income WHERE id=? AND user_id=?", (txn_id, user_id), one=True)
        if row:
            return jsonify({
                'id': row['id'], 'type': 'income', 'category': row['source'],
                'description': row['notes'] or '', 'amount': row['amount'], 'date': row['date']
            })
    else:
        row = query_db("SELECT * FROM expenses WHERE id=? AND user_id=?", (txn_id, user_id), one=True)
        if row:
            return jsonify({
                'id': row['id'], 'type': 'expense', 'category': row['category'],
                'description': row['description'] or '', 'amount': row['amount'], 'date': row['date']
            })
    return jsonify({'error': 'Not found'}), 404
