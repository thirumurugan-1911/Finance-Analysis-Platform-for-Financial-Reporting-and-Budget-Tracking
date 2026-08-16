"""
Authentication Module - User Registration, Login, Profile Management
Milestone 1 - Day 1 & 2
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.db import query_db, execute_db
from utils.helpers import hash_password, verify_password, login_required, get_current_date

bp = Blueprint('auth', __name__, url_prefix='')


@bp.route('/')
@bp.route('/index')
def index():
    """Landing page - redirects to dashboard if logged in."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()
        occupation = request.form.get('occupation', '').strip()
        monthly_income = float(request.form.get('monthly_income', 0) or 0)
        age = int(request.form.get('age', 0) or 0)

        # Validation
        if not name or not email or not password:
            flash('Name, Email, and Password are required.', 'danger')
            return render_template('register.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('register.html')

        existing = query_db('SELECT id FROM users WHERE email = ?', (email,), one=True)
        if existing:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('auth.login'))

        execute_db(
            """INSERT INTO users (name, email, password, phone, occupation, monthly_income, age)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (name, email, hash_password(password), phone, occupation, monthly_income, age)
        )
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = query_db('SELECT * FROM users WHERE email = ?', (email,), one=True)
        if user and verify_password(password, user['password']):
            session.clear()
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session.permanent = True
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('dashboard.index'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')


@bp.route('/logout')
def logout():
    """User logout."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and edit user profile."""
    user_id = session['user_id']
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        occupation = request.form.get('occupation', '').strip()
        monthly_income = float(request.form.get('monthly_income', 0) or 0)
        age = int(request.form.get('age', 0) or 0)

        execute_db(
            """UPDATE users SET name=?, phone=?, occupation=?, monthly_income=?, age=? WHERE id=?""",
            (name, phone, occupation, monthly_income, age, user_id)
        )
        session['user_name'] = name
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))

    user = query_db('SELECT * FROM users WHERE id = ?', (user_id,), one=True)
    return render_template('profile.html', user=user)


@bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password."""
    user_id = session['user_id']
    current = request.form.get('current_password', '')
    new = request.form.get('new_password', '')
    confirm = request.form.get('confirm_password', '')

    user = query_db('SELECT password FROM users WHERE id = ?', (user_id,), one=True)
    if not user or not verify_password(current, user['password']):
        flash('Current password is incorrect.', 'danger')
    elif len(new) < 6:
        flash('New password must be at least 6 characters.', 'danger')
    elif new != confirm:
        flash('New passwords do not match.', 'danger')
    else:
        execute_db('UPDATE users SET password=? WHERE id=?', (hash_password(new), user_id))
        flash('Password changed successfully!', 'success')
    return redirect(url_for('auth.profile'))
