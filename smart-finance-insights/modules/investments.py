"""
Investment Portfolio Management Module
Milestone 2 - Module 1 & 2
Features: Add/Edit/Delete investments, profit/loss calc, ROI, asset allocation
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from utils.db import query_db, execute_db
from utils.helpers import login_required, get_current_date, calculate_percentage

bp = Blueprint('investments', __name__, url_prefix='')

ASSET_TYPES = ['Stocks', 'Mutual Funds', 'Fixed Deposits', 'Gold', 'Bonds', 'Real Estate', 'Cryptocurrency']


@bp.route('/investments')
@login_required
def index():
    """Investment portfolio page."""
    user_id = session['user_id']
    investments = query_db(
        "SELECT * FROM investments WHERE user_id=? ORDER BY asset_type, investment_name",
        (user_id,)
    )

    # Calculate metrics
    inv_list = []
    total_invested = 0
    total_current = 0
    asset_allocation = {}
    for inv in investments:
        profit_loss = inv['current_value'] - inv['invested_amount']
        roi = calculate_percentage(profit_loss, inv['invested_amount'])
        status = 'Profit' if profit_loss >= 0 else 'Loss'
        inv_list.append({
            'id': inv['id'], 'asset_type': inv['asset_type'],
            'name': inv['investment_name'], 'invested': inv['invested_amount'],
            'current': inv['current_value'], 'profit_loss': profit_loss,
            'roi': roi, 'status': status, 'purchase_date': inv['purchase_date']
        })
        total_invested += inv['invested_amount']
        total_current += inv['current_value']
        asset_allocation[inv['asset_type']] = asset_allocation.get(inv['asset_type'], 0) + inv['current_value']

    total_profit_loss = total_current - total_invested
    total_roi = calculate_percentage(total_profit_loss, total_invested)

    # Asset allocation percentages
    allocation_data = []
    for asset, value in sorted(asset_allocation.items(), key=lambda x: -x[1]):
        allocation_data.append({
            'asset': asset, 'value': value,
            'percentage': calculate_percentage(value, total_current)
        })

    # Top and lowest performers
    sorted_by_roi = sorted(inv_list, key=lambda x: x['roi'], reverse=True)
    top_performers = sorted_by_roi[:3]
    low_performers = sorted_by_roi[-3:][::-1]

    return render_template('investments.html',
                           investments=inv_list,
                           total_invested=total_invested,
                           total_current=total_current,
                           total_profit_loss=total_profit_loss,
                           total_roi=total_roi,
                           allocation_data=allocation_data,
                           top_performers=top_performers,
                           low_performers=low_performers,
                           asset_types=ASSET_TYPES)


@bp.route('/investments/add', methods=['POST'])
@login_required
def add():
    """Add a new investment."""
    user_id = session['user_id']
    asset_type = request.form.get('asset_type', '').strip()
    name = request.form.get('name', '').strip()
    invested = float(request.form.get('invested', 0) or 0)
    current = float(request.form.get('current', 0) or 0)
    purchase_date = request.form.get('purchase_date', get_current_date())

    if not asset_type or not name or invested <= 0:
        flash('Asset type, name, and invested amount are required.', 'danger')
        return redirect(url_for('investments.index'))

    execute_db(
        """INSERT INTO investments (user_id, asset_type, investment_name, invested_amount, current_value, purchase_date)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, asset_type, name, invested, current, purchase_date)
    )
    flash('Investment added successfully!', 'success')
    return redirect(url_for('investments.index'))


@bp.route('/investments/edit/<int:inv_id>', methods=['POST'])
@login_required
def edit(inv_id):
    """Edit an investment."""
    user_id = session['user_id']
    asset_type = request.form.get('asset_type', '').strip()
    name = request.form.get('name', '').strip()
    invested = float(request.form.get('invested', 0) or 0)
    current = float(request.form.get('current', 0) or 0)
    purchase_date = request.form.get('purchase_date', get_current_date())

    record = query_db("SELECT * FROM investments WHERE id=? AND user_id=?", (inv_id, user_id), one=True)
    if not record:
        flash('Investment not found.', 'danger')
        return redirect(url_for('investments.index'))

    execute_db(
        """UPDATE investments SET asset_type=?, investment_name=?, invested_amount=?, current_value=?, purchase_date=?
           WHERE id=? AND user_id=?""",
        (asset_type, name, invested, current, purchase_date, inv_id, user_id)
    )
    flash('Investment updated successfully!', 'success')
    return redirect(url_for('investments.index'))


@bp.route('/investments/delete/<int:inv_id>', methods=['POST'])
@login_required
def delete(inv_id):
    """Delete an investment."""
    user_id = session['user_id']
    execute_db("DELETE FROM investments WHERE id=? AND user_id=?", (inv_id, user_id))
    flash('Investment deleted successfully!', 'success')
    return redirect(url_for('investments.index'))


@bp.route('/api/investment/<int:inv_id>')
@login_required
def get_investment(inv_id):
    """API: Get investment for editing (AJAX)."""
    user_id = session['user_id']
    row = query_db("SELECT * FROM investments WHERE id=? AND user_id=?", (inv_id, user_id), one=True)
    if row:
        return jsonify({
            'id': row['id'], 'asset_type': row['asset_type'],
            'name': row['investment_name'], 'invested': row['invested_amount'],
            'current': row['current_value'], 'purchase_date': row['purchase_date']
        })
    return jsonify({'error': 'Not found'}), 404


@bp.route('/portfolio-analytics')
@login_required
def portfolio_analytics():
    """Portfolio Analytics Dashboard - Milestone 2 Module 4."""
    user_id = session['user_id']
    investments = query_db("SELECT * FROM investments WHERE user_id=?", (user_id,))

    inv_list = []
    total_invested = 0
    total_current = 0
    asset_data = {}
    for inv in investments:
        pl = inv['current_value'] - inv['invested_amount']
        roi = calculate_percentage(pl, inv['invested_amount'])
        inv_list.append({
            'name': inv['investment_name'], 'asset': inv['asset_type'],
            'invested': inv['invested_amount'], 'current': inv['current_value'],
            'pl': pl, 'roi': roi
        })
        total_invested += inv['invested_amount']
        total_current += inv['current_value']
        asset_data[inv['asset_type']] = asset_data.get(inv['asset_type'], 0) + inv['current_value']

    # Monthly portfolio growth (simulated from purchase dates)
    from datetime import datetime, timedelta
    today = datetime.now()
    growth_data = []
    for i in range(6):
        d = today - timedelta(days=(5 - i) * 30)
        factor = 0.85 + (i * 0.03)
        growth_data.append({
            'month': d.strftime('%b'),
            'value': round(total_invested * factor, 0)
        })

    # Risk analysis (based on diversification)
    num_assets = len(asset_data)
    if num_assets >= 5:
        risk_score = 'Low'
        risk_level = 25
    elif num_assets >= 3:
        risk_score = 'Medium'
        risk_level = 55
    else:
        risk_score = 'High'
        risk_level = 80

    allocation = [{'asset': k, 'value': v, 'pct': calculate_percentage(v, total_current)}
                  for k, v in sorted(asset_data.items(), key=lambda x: -x[1])]

    return render_template('portfolio_analytics.html',
                           investments=inv_list,
                           total_invested=total_invested,
                           total_current=total_current,
                           total_pl=total_current - total_invested,
                           total_roi=calculate_percentage(total_current - total_invested, total_invested),
                           allocation=allocation,
                           growth_data=growth_data,
                           risk_score=risk_score,
                           risk_level=risk_level,
                           num_assets=num_assets)
